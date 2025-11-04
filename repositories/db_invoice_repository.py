from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
import uuid

from models.invoice import Invoice, InvoiceLine
from models.db_models import InvoiceDB, InvoiceLineDB


class InvoiceRepositoryDB:
    """Dépôt des factures et lignes de facture (SQLAlchemy)."""
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, invoice: Invoice):
        """Crée une facture et ses lignes dans une transaction."""
        with self._session_factory.begin() as s:
            s.add(InvoiceDB(
                id=invoice.id,
                order_id=invoice.order_id,
                user_id=invoice.user_id,
                total_cents=invoice.total_cents,
                issued_at=invoice.issued_at,
            ))
            for l in invoice.lines:
                s.add(InvoiceLineDB(
                    id=str(uuid.uuid4()),
                    invoice_id=invoice.id,
                    product_id=l.product_id,
                    name=l.name,
                    unit_price_cents=l.unit_price_cents,
                    quantity=l.quantity,
                ))

    def get(self, invoice_id: str) -> Optional[Invoice]:
        """Récupère une facture complète par identifiant."""
        with self._session_factory() as s:
            r = s.get(InvoiceDB, invoice_id)
            if not r:
                return None
            lines = s.scalars(select(InvoiceLineDB).where(InvoiceLineDB.invoice_id == r.id)).all()
            return Invoice(
                id=r.id,
                order_id=r.order_id,
                user_id=r.user_id,
                lines=[InvoiceLine(product_id=x.product_id, name=x.name, unit_price_cents=x.unit_price_cents, quantity=x.quantity) for x in lines],
                total_cents=r.total_cents,
                issued_at=r.issued_at,
            )

    def list_all(self) -> list[Invoice]:
        """Liste toutes les factures avec leurs lignes."""
        with self._session_factory() as s:
            rows = s.scalars(select(InvoiceDB)).all()
            result: list[Invoice] = []
            for r in rows:
                lines = s.scalars(select(InvoiceLineDB).where(InvoiceLineDB.invoice_id == r.id)).all()
                result.append(Invoice(
                    id=r.id,
                    order_id=r.order_id,
                    user_id=r.user_id,
                    lines=[InvoiceLine(product_id=x.product_id, name=x.name, unit_price_cents=x.unit_price_cents, quantity=x.quantity) for x in lines],
                    total_cents=r.total_cents,
                    issued_at=r.issued_at,
                ))
            return result
"""Dépôt SQLAlchemy des factures et de leurs lignes."""
