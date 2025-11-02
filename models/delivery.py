from dataclasses import dataclass
from typing import Optional


@dataclass
class Delivery:
    """
    Information de livraison d'une commande.
    
    Attributes:
        id: Identifiant unique de la livraison
        order_id: Référence de la commande
        carrier: Transporteur (ex: "POSTE")
        tracking_number: Numéro de suivi
        address: Adresse de livraison
        status: État de la livraison ("PREPAREE", "EN_COURS", "LIVREE")
    """
    id: str
    order_id: str
    carrier: str
    tracking_number: Optional[str]
    address: str
    status: str
