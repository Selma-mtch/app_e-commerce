from ast import Dict
from typing import Optional

from models.payment import Payment


class PaymentRepository:
    """
    Gère le stockage des paiements.
    """
    
    def __init__(self):
        self._by_id: Dict[str, Payment] = {}

    def add(self, payment: Payment):
        """Enregistre un nouveau paiement."""
        self._by_id[payment.id] = payment

    def get(self, payment_id: str) -> Optional[Payment]:
        """Récupère un paiement par son ID."""
        return self._by_id.get(payment_id)