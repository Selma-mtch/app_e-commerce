from typing import List  # not used directly; kept for compatibility
from dataclasses import dataclass


@dataclass
class InvoiceLine:
    """
    Ligne de facture.
    
    Attributes:
        product_id: Référence du produit
        name: Nom du produit
        unit_price_cents: Prix unitaire
        quantity: Quantité
    """
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int


@dataclass
class Invoice:
    """
    Facture générée pour une commande.
    
    Attributes:
        id: Identifiant unique de la facture
        order_id: Référence de la commande associée
        user_id: Référence de l'utilisateur
        lines: Lignes de la facture
        total_cents: Montant total en centimes
        issued_at: Timestamp d'émission
    """
    id: str
    order_id: str
    user_id: str
    lines: list[InvoiceLine]
    total_cents: int
    issued_at: float

