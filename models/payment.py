from dataclasses import dataclass


@dataclass
class Payment:
    """
    Paiement effectué pour une commande.
    
    Attributes:
        id: Identifiant unique du paiement
        order_id: Référence de la commande
        user_id: Référence de l'utilisateur
        amount_cents: Montant en centimes
        provider: Prestataire de paiement (ex: "CB")
        provider_ref: Référence de transaction du prestataire
        succeeded: Indique si le paiement a réussi
        created_at: Timestamp de création
    """
    id: str
    order_id: str
    user_id: str
    amount_cents: int
    provider: str
    provider_ref: str
    succeeded: bool
    created_at: float
