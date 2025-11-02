"""
main.py - Point d'entrée du projet E-commerce
==============================================

Script de démonstration qui illustre le fonctionnement complet
de l'application e-commerce avec un scénario réaliste.

Scénario:
1. Initialisation des repositories et services
2. Création de produits dans le catalogue
3. Inscription d'un administrateur et d'un client
4. Connexion du client
5. Navigation dans le catalogue
6. Ajout de produits au panier
7. Passage de commande (checkout)
8. Validation de la commande par l'admin
9. Paiement par carte bancaire
10. Expédition de la commande
11. Marquage de la livraison
12. Ouverture d'un ticket support client
13. Échanges de messages
14. Fermeture du ticket
15. Déconnexion

Usage:
    python main.py
"""

from __future__ import annotations
import uuid

# Import des modèles
from models.user import User
from models.product import Product

# Import des repositories
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from repositories.cart_repository import CartRepository
from repositories.order_repository import OrderRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.payment_repository import PaymentRepository
from repositories.thread_repository import ThreadRepository

# Import des services
from services.auth.session_manager import SessionManager
from services.auth.auth_service import AuthService
from services.catalog_service import CatalogService
from services.cart_service import CartService
from services.order_service import OrderService
from services.billing_service import BillingService
from services.delivery_service import DeliveryService
from services.payment_gateway import PaymentGateway
from services.customer_service import CustomerService


def print_separator(title: str = ""):
    """Affiche un séparateur visuel."""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print('=' * 60)
    else:
        print("-" * 60)


def main():
    """
    Fonction principale qui exécute le scénario de démonstration.
    """
    print("=" * 60)
    print(" 🛒 DÉMONSTRATION APPLICATION E-COMMERCE")
    print("=" * 60)
    
    # =========================
    # 1. INITIALISATION
    # =========================
    print_separator("1. INITIALISATION DES SERVICES")
    
    # Création des repositories
    users = UserRepository()
    products = ProductRepository()
    carts = CartRepository()
    orders = OrderRepository()
    invoices = InvoiceRepository()
    payments = PaymentRepository()
    threads = ThreadRepository()
    sessions = SessionManager()
    
    # Création des services
    auth = AuthService(users, sessions)
    catalog = CatalogService(products)
    cart_svc = CartService(carts, products)
    billing = BillingService(invoices)
    delivery_svc = DeliveryService()
    gateway = PaymentGateway()
    order_svc = OrderService(
        orders, products, carts, payments, invoices,
        billing, delivery_svc, gateway, users
    )
    cs = CustomerService(threads, users)
    
    print("✓ Tous les services sont initialisés")
    
    # =========================
    # 2. CRÉATION DU CATALOGUE
    # =========================
    print_separator("2. CRÉATION DU CATALOGUE PRODUITS")
    
    p1 = Product(
        id=str(uuid.uuid4()),
        name="T-Shirt Logo",
        description="T-shirt en coton bio avec logo",
        price_cents=1999,  # 19.99€
        stock_qty=100
    )
    
    p2 = Product(
        id=str(uuid.uuid4()),
        name="Sweat à Capuche",
        description="Sweat confortable en molleton",
        price_cents=4999,  # 49.99€
        stock_qty=50
    )
    
    p3 = Product(
        id=str(uuid.uuid4()),
        name="Jean Slim",
        description="Jean stretch confortable",
        price_cents=7999,  # 79.99€
        stock_qty=30
    )
    
    products.add(p1)
    products.add(p2)
    products.add(p3)
    
    print(f"✓ {len(catalog.list_products())} produits ajoutés au catalogue")
    for p in catalog.list_products():
        print(f"  - {p.name}: {p.price_cents/100:.2f}€ (stock: {p.stock_qty})")
    
    # =========================
    # 3. INSCRIPTION DES UTILISATEURS
    # =========================
    print_separator("3. INSCRIPTION DES UTILISATEURS")
    
    # Création d'un administrateur
    admin = auth.register(
        email="admin@shop.test",
        password="admin_secure_123",
        first_name="Admin",
        last_name="Root",
        address="1 Rue du Back Office, 75001 Paris",
        is_admin=True
    )
    print(f"✓ Administrateur créé: {admin.first_name} {admin.last_name}")
    print(f"  Email: {admin.email}")
    
    # Création d'un client
    client = auth.register(
        email="alice.martin@email.test",
        password="client_secure_456",
        first_name="Alice",
        last_name="Martin",
        address="12 Rue des Fleurs, 69002 Lyon"
    )
    print(f"✓ Client créé: {client.first_name} {client.last_name}")
    print(f"  Email: {client.email}")
    print(f"  Adresse: {client.address}")
    
    # =========================
    # 4. CONNEXION DU CLIENT
    # =========================
    print_separator("4. CONNEXION DU CLIENT")
    
    token = auth.login("alice.martin@email.test", "client_secure_456")
    user_id = sessions.get_user_id(token)
    
    print(f"✓ Client connecté avec succès")
    print(f"  Token de session: {token[:20]}...")
    print(f"  User ID: {user_id}")
    
    # =========================
    # 5. AFFICHAGE DU CATALOGUE
    # =========================
    print_separator("5. NAVIGATION DANS LE CATALOGUE")
    
    available_products = catalog.list_products()
    print(f"📦 {len(available_products)} produits disponibles:")
    for i, p in enumerate(available_products, 1):
        print(f"  {i}. {p.name}")
        print(f"     {p.description}")
        print(f"     Prix: {p.price_cents/100:.2f}€")
        print(f"     En stock: {p.stock_qty} unités")
        print()
    
    # =========================
    # 6. AJOUT AU PANIER
    # =========================
    print_separator("6. AJOUT DE PRODUITS AU PANIER")
    
    # Alice ajoute 2 T-shirts
    cart_svc.add_to_cart(user_id, p1.id, 2)
    print(f"✓ Ajouté au panier: 2x {p1.name}")
    
    # Alice ajoute 1 sweat
    cart_svc.add_to_cart(user_id, p2.id, 1)
    print(f"✓ Ajouté au panier: 1x {p2.name}")
    
    # Affichage du panier
    cart = cart_svc.view_cart(user_id)
    total = cart_svc.cart_total(user_id)
    
    print(f"\n🛒 Contenu du panier:")
    for item in cart.items.values():
        prod = products.get(item.product_id)
        print(f"  - {prod.name} x{item.quantity} = {prod.price_cents * item.quantity / 100:.2f}€")
    print(f"\n  💰 TOTAL: {total/100:.2f}€")
    
    # =========================
    # 7. PASSAGE DE COMMANDE
    # =========================
    print_separator("7. PASSAGE DE COMMANDE (CHECKOUT)")
    
    order = order_svc.checkout(user_id)
    
    print(f"✓ Commande créée avec succès")
    print(f"  ID commande: {order.id}")
    print(f"  Statut: {order.status.name}")
    print(f"  Montant total: {order.total_cents()/100:.2f}€")
    print(f"  Articles:")
    for item in order.items:
        print(f"    - {item.name} x{item.quantity} = {item.unit_price_cents * item.quantity / 100:.2f}€")
    
    # Vérification que le panier est vide
    cart_after = cart_svc.view_cart(user_id)
    print(f"\n✓ Panier vidé automatiquement ({len(cart_after.items)} articles restants)")
    
    # Vérification du stock réservé
    print(f"\n✓ Stock réservé:")
    for item in order.items:
        prod = products.get(item.product_id)
        print(f"  - {prod.name}: {prod.stock_qty} unités restantes")
    
    # =========================
    # 8. VALIDATION PAR L'ADMIN
    # =========================
    print_separator("8. VALIDATION DE LA COMMANDE (BACKOFFICE)")
    
    order = order_svc.backoffice_validate_order(admin.id, order.id)
    
    print(f"✓ Commande validée par l'administrateur")
    print(f"  Statut: {order.status.name}")
    print(f"  Validée le: {order.validated_at}")
    
    # =========================
    # 9. PAIEMENT
    # =========================
    print_separator("9. PAIEMENT PAR CARTE BANCAIRE")
    
    print("💳 Informations de paiement:")
    print("  Carte: 4242 4242 4242 4242")
    print("  Expiration: 12/2030")
    print("  CVC: 123")
    
    try:
        payment = order_svc.pay_by_card(
            order.id,
            card_number="4242424242424242",
            exp_month=12,
            exp_year=2030,
            cvc="123"
        )
        
        print(f"\n✓ Paiement accepté!")
        print(f"  ID paiement: {payment.id}")
        print(f"  Montant: {payment.amount_cents/100:.2f}€")
        print(f"  Référence PSP: {payment.provider_ref}")
        print(f"  Provider: {payment.provider}")
        
        # Récupération de la commande mise à jour
        order = order_svc.orders.get(order.id)
        print(f"\n✓ Commande mise à jour:")
        print(f"  Statut: {order.status.name}")
        print(f"  ID facture: {order.invoice_id}")
        
        # Affichage de la facture
        if order.invoice_id:
            invoice = invoices.get(order.invoice_id)
            print(f"\n📄 Facture générée:")
            print(f"  ID: {invoice.id}")
            print(f"  Total: {invoice.total_cents/100:.2f}€")
            print(f"  Lignes:")
            for line in invoice.lines:
                print(f"    - {line.name} x{line.quantity} = {line.unit_price_cents * line.quantity / 100:.2f}€")
        
    except ValueError as e:
        print(f"❌ Erreur de paiement: {e}")
        return
    
    # =========================
    # 10. EXPÉDITION
    # =========================
    print_separator("10. EXPÉDITION DE LA COMMANDE")
    
    order = order_svc.backoffice_ship_order(admin.id, order.id)
    
    print(f"✓ Commande expédiée")
    print(f"  Statut: {order.status.name}")
    print(f"  Transporteur: {order.delivery.carrier}")
    print(f"  Numéro de suivi: {order.delivery.tracking_number}")
    print(f"  Adresse de livraison: {order.delivery.address}")
    print(f"  Statut livraison: {order.delivery.status}")
    
    # =========================
    # 11. LIVRAISON
    # =========================
    print_separator("11. MARQUAGE DE LA LIVRAISON")
    
    order = order_svc.backoffice_mark_delivered(admin.id, order.id)
    
    print(f"✓ Commande marquée comme livrée")
    print(f"  Statut commande: {order.status.name}")
    print(f"  Statut livraison: {order.delivery.status}")
    print(f"  Livrée le: {order.delivered_at}")
    
    # =========================
    # 12. SERVICE CLIENT
    # =========================
    print_separator("12. OUVERTURE D'UN TICKET SUPPORT")
    
    # Le client ouvre un ticket
    thread = cs.open_thread(
        user_id=user_id,
        subject="Taille du T-shirt trop petite",
        order_id=order.id
    )
    
    print(f"✓ Ticket support créé")
    print(f"  ID: {thread.id}")
    print(f"  Sujet: {thread.subject}")
    print(f"  Commande liée: {thread.order_id}")
    
    # =========================
    # 13. ÉCHANGES DE MESSAGES
    # =========================
    print_separator("13. ÉCHANGES AVEC LE SUPPORT")
    
    # Message du client
    msg1 = cs.post_message(
        thread_id=thread.id,
        author_user_id=user_id,
        body="Bonjour, j'ai reçu ma commande mais le T-shirt est trop petit. "
             "Je souhaiterais échanger pour une taille au-dessus. Comment puis-je procéder ?"
    )
    print(f"💬 Message client envoyé:")
    print(f"   \"{msg1.body}\"")
    
    # Réponse de l'agent support
    msg2 = cs.post_message(
        thread_id=thread.id,
        author_user_id=None,  # None = agent support
        body="Bonjour Alice, nous sommes désolés pour ce désagrément. "
             "Nous pouvons vous proposer un échange gratuit. Merci de nous renvoyer "
             "l'article à l'adresse indiquée dans votre email de confirmation. "
             "Nous vous enverrons la nouvelle taille dès réception."
    )
    print(f"\n🎧 Réponse du support:")
    print(f"   \"{msg2.body}\"")
    
    # Confirmation du client
    msg3 = cs.post_message(
        thread_id=thread.id,
        author_user_id=user_id,
        body="Parfait, merci beaucoup ! Je vais procéder au retour dès demain."
    )
    print(f"\n💬 Message client:")
    print(f"   \"{msg3.body}\"")
    
    print(f"\n✓ {len(thread.messages)} messages échangés dans le fil")
    
    # =========================
    # 14. FERMETURE DU TICKET
    # =========================
    print_separator("14. CLÔTURE DU TICKET")
    
    thread = cs.close_thread(thread.id, admin.id)
    
    print(f"✓ Ticket fermé par l'administrateur")
    print(f"  Statut: {'Fermé' if thread.closed else 'Ouvert'}")
    
    # =========================
    # 15. RÉSUMÉ ET DÉCONNEXION
    # =========================
    print_separator("15. RÉSUMÉ DE LA SESSION")
    
    # Liste des commandes du client
    client_orders = order_svc.view_orders(user_id)
    print(f"📋 Commandes de {client.first_name} {client.last_name}:")
    for o in client_orders:
        print(f"  - Commande {o.id[:8]}...")
        print(f"    Statut: {o.status.name}")
        print(f"    Total: {o.total_cents()/100:.2f}€")
        print(f"    Articles: {len(o.items)}")
        if o.delivery:
            print(f"    Suivi: {o.delivery.tracking_number}")
    
    # Liste des tickets support
    client_threads = cs.list_user_threads(user_id)
    print(f"\n💬 Tickets support:")
    for t in client_threads:
        print(f"  - {t.subject}")
        print(f"    Messages: {len(t.messages)}")
        print(f"    Statut: {'Fermé' if t.closed else 'Ouvert'}")
    
    # Déconnexion
    auth.logout(token)
    print(f"\n✓ Client déconnecté")
    
    # =========================
    # FIN
    # =========================
    print_separator()
    print("\n✨ DÉMONSTRATION TERMINÉE AVEC SUCCÈS ✨\n")
    print("📊 Statistiques de la session:")
    print(f"  - Utilisateurs inscrits: {len(users._by_id)}")
    print(f"  - Produits au catalogue: {len(products._by_id)}")
    print(f"  - Commandes passées: {len(orders._by_id)}")
    print(f"  - Paiements effectués: {len(payments._by_id)}")
    print(f"  - Factures émises: {len(invoices._by_id)}")
    print(f"  - Tickets support: {len(threads._by_id)}")
    print()


if __name__ == "__main__":
    """
    Point d'entrée du programme.
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programme interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()