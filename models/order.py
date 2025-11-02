from ast import List
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from models.delivery import Delivery


class OrderStatus(Enum):
    """États possibles d'une commande."""
    CREE = auto()
    VALIDEE = auto()
    PAYEE = auto()
    EXPEDIEE = auto()
    LIVREE = auto()
    ANNULEE = auto()
    REMBOURSEE = auto()

@dataclass
class OrderItem:
    """
    Ligne d'article dans une commande.
    
    Attributes:
        product_id: Référence du produit
        name: Nom du produit (capturé au moment de la commande)
        unit_price_cents: Prix unitaire en centimes
        quantity: Quantité commandée
    """
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int

@dataclass
class Order:
    """
    Commande passée par un utilisateur.
    
    Attributes:
        id: Identifiant unique de la commande
        user_id: Référence de l'utilisateur
        items: Articles commandés
        status: État actuel de la commande
        created_at: Date de création
        validated_at: Date de validation par l'admin
        paid_at: Date de paiement
        shipped_at: Date d'expédition
        delivered_at: Date de livraison
        cancelled_at: Date d'annulation
        refunded_at: Date de remboursement
        delivery: Information de livraison
        invoice_id: Référence de la facture
        payment_id: Référence du paiement
    """
    id: str
    user_id: str
    items: list[OrderItem]
    status: OrderStatus
    created_at: float
    validated_at: Optional[float] = None
    paid_at: Optional[float] = None
    shipped_at: Optional[float] = None
    delivered_at: Optional[float] = None
    cancelled_at: Optional[float] = None
    refunded_at: Optional[float] = None
    delivery: Optional[Delivery] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None

    def total_cents(self) -> int:
        """
        Calcule le montant total de la commande.
        
        Returns:
            Total en centimes
        """
        return sum(i.unit_price_cents * i.quantity for i in self.items)