from typing import Dict, List, Optional

from models.order import Order


class OrderRepository:
    """
    Gère le stockage des commandes.
    """
    
    def __init__(self):
        self._by_id: Dict[str, Order] = {}
        self._by_user: Dict[str, List[str]] = {}

    def add(self, order: Order):
        """Ajoute une nouvelle commande."""
        self._by_id[order.id] = order
        self._by_user.setdefault(order.user_id, []).append(order.id)

    def get(self, order_id: str) -> Optional[Order]:
        """Récupère une commande par son ID."""
        return self._by_id.get(order_id)

    def list_by_user(self, user_id: str) -> list[Order]:
        """Liste toutes les commandes d'un utilisateur."""
        return [self._by_id[oid] for oid in self._by_user.get(user_id, [])]

    def update(self, order: Order):
        """Met à jour une commande existante."""
        self._by_id[order.id] = order
