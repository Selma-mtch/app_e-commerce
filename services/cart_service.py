from models.product import Cart
from repositories.cart_repository import CartRepository
from repositories.product_repository import ProductRepository


class CartService:
    """
    Service de gestion du panier d'achat.
    """
    
    def __init__(self, carts: CartRepository, products: ProductRepository):
        self.carts = carts
        self.products = products

    def add_to_cart(self, user_id: str, product_id: str, qty: int = 1):
        """
        Ajoute un produit au panier.
        
        Raises:
            ValueError: Si le produit n'existe pas
        """
        product = self.products.get(product_id)
        if not product:
            raise ValueError("Produit introuvable.")
        # Si le repository supporte une persistance, utiliser son API
        if hasattr(self.carts, 'add_item'):
            self.carts.add_item(user_id, product_id, qty)
        else:
            self.carts.get_or_create(user_id).add(product, qty)

    def remove_from_cart(self, user_id: str, product_id: str, qty: int = 1):
        """Retire un produit du panier."""
        if hasattr(self.carts, 'remove_item'):
            self.carts.remove_item(user_id, product_id, qty)
        else:
            self.carts.get_or_create(user_id).remove(product_id, qty)

    def view_cart(self, user_id: str) -> Cart:
        """Affiche le panier d'un utilisateur."""
        return self.carts.get_or_create(user_id)

    def cart_total(self, user_id: str) -> int:
        """Calcule le total du panier en centimes."""
        return self.carts.get_or_create(user_id).total_cents(self.products)

    def set_quantity(self, user_id: str, product_id: str, qty: int) -> None:
        """
        Met à jour directement la quantité d'un article dans le panier.

        Si ``qty <= 0``, l'article est retiré.
        """
        # Valide que le produit existe (comportement aligné avec add_to_cart)
        product = self.products.get(product_id)
        if not product:
            raise ValueError("Produit introuvable.")

        # Délègue au dépôt s'il expose une API dédiée, sinon met à jour le Cart en mémoire
        if hasattr(self.carts, "set_quantity"):
            self.carts.set_quantity(user_id, product_id, qty)
            return

        cart = self.carts.get_or_create(user_id)
        if qty <= 0:
            cart.remove(product_id, qty=0)
        else:
            cart.items[product_id] = CartItem(product_id=product_id, quantity=qty)