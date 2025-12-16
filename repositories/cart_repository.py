from typing import Dict

from models.product import Cart, CartItem


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

    def remove_product_everywhere(self, product_id: str) -> int:
        """
        Retire un produit de tous les paniers.

        Args:
            product_id: Identifiant du produit à retirer

        Returns:
            Nombre de paniers affectés
        """
        affected = 0
        for cart in self._by_user.values():
            if product_id in cart.items:
                del cart.items[product_id]
                affected += 1
        return affected

    def set_quantity(self, user_id: str, product_id: str, qty: int) -> None:
        """
        Définit explicitement la quantité pour un produit dans le panier.

        Si ``qty <= 0``, l'article est retiré du panier.
        """
        cart = self.get_or_create(user_id)
        if qty <= 0:
            cart.remove(product_id, qty=0)
            return

        # Met à jour ou crée l'item avec la quantité demandée
        cart.items[product_id] = CartItem(product_id=product_id, quantity=qty)

    # API complémentaire pour compat avec une implémentation DB
    def add_item(self, user_id: str, product_id: str, qty: int = 1):
        cart = self.get_or_create(user_id)
        from models.product import Product
        # Dans la version mémoire, on ne peut pas récupérer le Product ici sans repo.
        # Cette méthode n'est utilisée qu'à travers CartService qui valide déjà le produit.
        pseudo_product = Product(id=product_id, name='', description='', price_cents=0, stock_qty=10, active=True)
        cart.add(pseudo_product, qty)

    def remove_item(self, user_id: str, product_id: str, qty: int = 1):
        cart = self.get_or_create(user_id)
        cart.remove(product_id, qty)
