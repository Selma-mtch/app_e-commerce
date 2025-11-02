from __future__ import annotations

from ast import List
import time
from typing import Optional
import uuid
from models.order import Order, OrderItem, OrderStatus
from models.payment import Payment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repositories.order_repository import OrderRepository
    from repositories.cart_repository import CartRepository
    from repositories.invoice_repository import InvoiceRepository
    from repositories.order_repository import OrderRepository
    from repositories.payment_repository import PaymentRepository
    from repositories.product_repository import ProductRepository
    from services.billing_service import BillingService
    from services.delivery_service import DeliveryService
    from services.payment_gateway import PaymentGateway
    from repositories.user_repository import UserRepository



class OrderService:
    """
    Service principal de gestion des commandes.
    
    Orchestre le processus complet : création, paiement, expédition, livraison.
    """
    
    def __init__(
        self,
        orders: OrderRepository,
        products: ProductRepository,
        carts: CartRepository,
        payments: PaymentRepository,
        invoices: InvoiceRepository,
        billing: BillingService,
        delivery_svc: DeliveryService,
        gateway: PaymentGateway,
        users: UserRepository 
    ):
        self.orders = orders
        self.products = products
        self.carts = carts
        self.payments = payments
        self.invoices = invoices
        self.billing = billing
        self.delivery_svc = delivery_svc
        self.gateway = gateway
        self.users = users

    # ----- Opérations client -----

    def checkout(self, user_id: str) -> Order:
        """
        Transforme le panier en commande et réserve le stock.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            La commande créée
            
        Raises:
            ValueError: Si le panier est vide ou si un produit est indisponible
        """
        cart = self.carts.get_or_create(user_id)
        if not cart.items:
            raise ValueError("Panier vide.")
        
        # Réserver le stock
        order_items: List[OrderItem] = []
        for it in cart.items.values():
            p = self.products.get(it.product_id)
            if not p or not p.active:
                raise ValueError("Produit indisponible.")
            if p.stock_qty < it.quantity:
                raise ValueError(f"Stock insuffisant pour {p.name}.")
            
            self.products.reserve_stock(p.id, it.quantity)
            order_items.append(OrderItem(
                product_id=p.id,
                name=p.name,
                unit_price_cents=p.price_cents,
                quantity=it.quantity
            ))
        
        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            items=order_items,
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        self.orders.add(order)
        
        # Vider le panier
        self.carts.clear(user_id)
        return order

    def pay_by_card(self, order_id: str, card_number: str, exp_month: int, 
                    exp_year: int, cvc: str) -> Payment:
        """
        Effectue le paiement d'une commande par carte bancaire.
        
        Args:
            order_id: ID de la commande
            card_number: Numéro de carte
            exp_month: Mois d'expiration
            exp_year: Année d'expiration
            cvc: Code de sécurité
            
        Returns:
            L'objet Payment créé
            
        Raises:
            ValueError: Si la commande n'existe pas, a un mauvais statut ou si le paiement échoue
        """
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Commande introuvable.")
        if order.status not in {OrderStatus.CREE, OrderStatus.VALIDEE}:
            raise ValueError("Statut de commande incompatible avec le paiement.")
        
        amount = order.total_cents()
        res = self.gateway.charge_card(
            card_number, exp_month, exp_year, cvc, amount, 
            idempotency_key=order.id
        )
        
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=order.user_id,
            amount_cents=amount,
            provider="CB",
            provider_ref=res.get("transaction_id"),
            succeeded=res["success"],
            created_at=time.time()
        )
        self.payments.add(payment)
        
        if not payment.succeeded:
            raise ValueError("Paiement refusé.")
        
        # Mise à jour du statut de la commande
        order.payment_id = payment.id
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        
        # Génération de la facture
        inv = self.billing.issue_invoice(order)
        order.invoice_id = inv.id
        
        self.orders.update(order)
        return payment

    def view_orders(self, user_id: str) -> list[Order]:
        """
        Liste toutes les commandes d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des commandes
        """
        return self.orders.list_by_user(user_id)

    def request_cancellation(self, user_id: str, order_id: str) -> Order:
        """
        Demande d'annulation d'une commande par le client.
        
        Args:
            user_id: ID de l'utilisateur
            order_id: ID de la commande
            
        Returns:
            La commande annulée
            
        Raises:
            ValueError: Si la commande est introuvable ou déjà expédiée
        """
        order = self.orders.get(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Commande introuvable.")
        if order.status in {OrderStatus.EXPEDIEE, OrderStatus.LIVREE}:
            raise ValueError("Trop tard pour annuler : commande expédiée.")
        
        order.status = OrderStatus.ANNULEE
        order.cancelled_at = time.time()
        
        # Restituer le stock
        for it in order.items:
            self.products.release_stock(it.product_id, it.quantity)
        
        self.orders.update(order)
        return order

    # =========================
    # OPÉRATIONS BACKOFFICE (ADMIN)
    # =========================

    def backoffice_validate_order(self, admin_user_id: str, order_id: str) -> Order:
        """
        Validation d'une commande par un administrateur.
        
        Args:
            admin_user_id: ID de l'administrateur
            order_id: ID de la commande
            
        Returns:
            La commande validée
            
        Raises:
            PermissionError: Si l'utilisateur n'est pas admin
            ValueError: Si la commande n'existe pas ou a un mauvais statut
        """
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.CREE:
            raise ValueError("Commande introuvable ou mauvais statut.")
        
        order.status = OrderStatus.VALIDEE
        order.validated_at = time.time()
        self.orders.update(order)
        return order

    def backoffice_ship_order(self, admin_user_id: str, order_id: str) -> Order:
        """
        Expédition d'une commande par un administrateur.
        
        Args:
            admin_user_id: ID de l'administrateur
            order_id: ID de la commande
            
        Returns:
            La commande expédiée
            
        Raises:
            PermissionError: Si l'utilisateur n'est pas admin
            ValueError: Si la commande n'est pas payée
        """
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.PAYEE:
            raise ValueError("La commande doit être payée pour être expédiée.")
        
        user = self.users.get(order.user_id)
        delivery = self.delivery_svc.prepare_delivery(order, address=user.address)
        delivery = self.delivery_svc.ship(delivery)
        
        order.delivery = delivery
        order.status = OrderStatus.EXPEDIEE
        order.shipped_at = time.time()
        
        self.orders.update(order)
        return order

    def backoffice_mark_delivered(self, admin_user_id: str, order_id: str) -> Order:
        """
        Marquage d'une commande comme livrée.
        
        Args:
            admin_user_id: ID de l'administrateur
            order_id: ID de la commande
            
        Returns:
            La commande marquée comme livrée
            
        Raises:
            PermissionError: Si l'utilisateur n'est pas admin
            ValueError: Si la commande n'est pas expédiée
        """
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.EXPEDIEE or not order.delivery:
            raise ValueError("Commande non expédiée.")
        
        self.delivery_svc.mark_delivered(order.delivery)
        order.status = OrderStatus.LIVREE
        order.delivered_at = time.time()
        
        self.orders.update(order)
        return order

    def backoffice_refund(self, admin_user_id: str, order_id: str, 
                          amount_cents: Optional[int] = None) -> Order:
        """
        Remboursement d'une commande.
        
        Args:
            admin_user_id: ID de l'administrateur
            order_id: ID de la commande
            amount_cents: Montant à rembourser (None = montant total)
            
        Returns:
            La commande remboursée
            
        Raises:
            PermissionError: Si l'utilisateur n'est pas admin
            ValueError: Si le remboursement n'est pas autorisé
        """
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        
        order = self.orders.get(order_id)
        if not order or order.status not in {OrderStatus.PAYEE, OrderStatus.ANNULEE}:
            raise ValueError("Remboursement non autorisé au statut actuel.")
        
        amount = amount_cents or order.total_cents()
        
        # Remboursement via le PSP
        payment = self.payments.get(order.payment_id) if order.payment_id else None
        if not payment or not payment.provider_ref:
            raise ValueError("Aucun paiement initial.")
        
        self.gateway.refund(payment.provider_ref, amount)
        
        order.status = OrderStatus.REMBOURSEE
        order.refunded_at = time.time()
        
        # Restituer le stock
        for it in order.items:
            self.products.release_stock(it.product_id, it.quantity)
        
        self.orders.update(order)
        return order