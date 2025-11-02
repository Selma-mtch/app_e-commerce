import time
import uuid
from models.invoice import Invoice, InvoiceLine
from models.order import Order
from repositories.invoice_repository import InvoiceRepository


class BillingService:
    """
    Service de facturation.
    """
    
    def __init__(self, invoices: InvoiceRepository):
        self.invoices = invoices

    def issue_invoice(self, order: Order) -> Invoice:
        """
        Génère une facture pour une commande.
        
        Args:
            order: La commande à facturer
            
        Returns:
            La facture créée
        """
        lines = [
            InvoiceLine(
                product_id=i.product_id,
                name=i.name,
                unit_price_cents=i.unit_price_cents,
                quantity=i.quantity
            )
            for i in order.items
        ]
        
        inv = Invoice(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=order.user_id,
            lines=lines,
            total_cents=sum(l.unit_price_cents * l.quantity for l in lines),
            issued_at=time.time()
        )
        self.invoices.add(inv)
        return inv
