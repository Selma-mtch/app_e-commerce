import uuid
from models.delivery import Delivery
from models.order import Order


class DeliveryService:
    """
    Service de gestion des livraisons.
    """
    
    def prepare_delivery(self, order: Order, address: str, 
                        carrier: str = "POSTE") -> Delivery:
        """
        Prépare une livraison pour une commande.
        
        Args:
            order: La commande à livrer
            address: Adresse de livraison
            carrier: Transporteur
            
        Returns:
            L'objet Delivery créé
        """
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            carrier=carrier,
            tracking_number=None,
            address=address,
            status="PREPAREE"
        )
        return delivery

    def ship(self, delivery: Delivery) -> Delivery:
        """
        Marque une livraison comme expédiée et génère un numéro de suivi.
        
        Args:
            delivery: La livraison à expédier
            
        Returns:
            La livraison mise à jour
        """
        delivery.status = "EN_COURS"
        delivery.tracking_number = delivery.tracking_number or f"TRK-{uuid.uuid4().hex[:10].upper()}"
        return delivery

    def mark_delivered(self, delivery: Delivery) -> Delivery:
        """
        Marque une livraison comme livrée.
        
        Args:
            delivery: La livraison à marquer comme livrée
            
        Returns:
            La livraison mise à jour
        """
        delivery.status = "LIVREE"
        return delivery
