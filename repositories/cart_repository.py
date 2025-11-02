from ast import Dict

from models.product import Cart


class CartRepository:
    """
    Gère les paniers d'achat des utilisateurs.
    """
    
    def __init__(self):
        self._by_user: Dict[str, Cart] = {}

    def get_or_create(self, user_id: str) -> Cart:
        """Récupère ou crée un panier pour un utilisateur."""
        if user_id not in self._by_user:
            self._by_user[user_id] = Cart(user_id=user_id)
        return self._by_user[user_id]

    def clear(self, user_id: str):
        """Vide le panier d'un utilisateur."""
        self.get_or_create(user_id).clear()