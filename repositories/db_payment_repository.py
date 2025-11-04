from typing import Optional
from sqlalchemy.orm import sessionmaker

from models.payment import Payment
from models.db_models import PaymentDB


class PaymentRepositoryDB:
    """Dépôt des paiements (SQLAlchemy)."""
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, payment: Payment):
        """Enregistre un paiement (transaction)."""
        with self._session_factory.begin() as s:
            s.add(PaymentDB(
                id=payment.id,
                order_id=payment.order_id,
                user_id=payment.user_id,
                amount_cents=payment.amount_cents,
                provider=payment.provider,
                provider_ref=payment.provider_ref,
                succeeded=payment.succeeded,
                created_at=payment.created_at,
            ))

    def get(self, payment_id: str) -> Optional[Payment]:
        """Récupère un paiement par identifiant."""
        with self._session_factory() as s:
            r = s.get(PaymentDB, payment_id)
            if not r:
                return None
            return Payment(
                id=r.id,
                order_id=r.order_id,
                user_id=r.user_id,
                amount_cents=r.amount_cents,
                provider=r.provider,
                provider_ref=r.provider_ref or '',
                succeeded=r.succeeded,
                created_at=r.created_at,
            )

    def list_all(self) -> list[Payment]:
        """Liste tous les paiements."""
        with self._session_factory() as s:
            rows = s.query(PaymentDB).all()
            return [
                Payment(
                    id=r.id,
                    order_id=r.order_id,
                    user_id=r.user_id,
                    amount_cents=r.amount_cents,
                    provider=r.provider,
                    provider_ref=r.provider_ref or '',
                    succeeded=r.succeeded,
                    created_at=r.created_at,
                )
                for r in rows
            ]
"""Dépôt SQLAlchemy des paiements."""
