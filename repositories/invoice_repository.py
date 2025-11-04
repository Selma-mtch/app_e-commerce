from typing import Dict, Optional

from models.invoice import Invoice


class InvoiceRepository:
    """
    Gère le stockage des factures.
    """
    
    def __init__(self):
        self._by_id: Dict[str, Invoice] = {}

    def add(self, invoice: Invoice):
        """Ajoute une nouvelle facture."""
        self._by_id[invoice.id] = invoice

    def get(self, invoice_id: str) -> Optional[Invoice]:
        """Récupère une facture par son ID."""
        return self._by_id.get(invoice_id)

    def list_all(self) -> list[Invoice]:
        """Liste toutes les factures."""
        return list(self._by_id.values())
