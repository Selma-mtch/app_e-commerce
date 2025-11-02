from ast import Dict
import uuid


class PaymentGateway:
    """
    Simulation d'une passerelle de paiement (Stripe, Adyen, etc.).
    
    Note: Implémentation mock pour la démo.
    """
    
    def charge_card(self, card_number: str, exp_month: int, exp_year: int, 
                    cvc: str, amount_cents: int, idempotency_key: str) -> Dict:
        """
        Effectue un paiement par carte.
        
        Args:
            card_number: Numéro de carte
            exp_month: Mois d'expiration
            exp_year: Année d'expiration
            cvc: Code de sécurité
            amount_cents: Montant en centimes
            idempotency_key: Clé d'idempotence
            
        Returns:
            Dictionnaire avec success, transaction_id, failure_reason
        """
        # MOCK: succès si la carte ne finit pas par '0000'
        ok = not card_number.endswith("0000")
        return {
            "success": ok,
            "transaction_id": str(uuid.uuid4()) if ok else None,
            "failure_reason": None if ok else "CARTE_REFUSEE"
        }

    def refund(self, transaction_id: str, amount_cents: int) -> Dict:
        """
        Effectue un remboursement.
        
        Returns:
            Dictionnaire avec success et refund_id
        """
        return {
            "success": True,
            "refund_id": str(uuid.uuid4())
        }
