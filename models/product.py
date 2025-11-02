from ast import Dict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from repositories.product_repository import ProductRepository

@dataclass
class Product:
    """
    Représente un produit du catalogue.
    
    Attributes:
        id: Identifiant unique du produit
        name: Nom du produit
        description: Description détaillée
        price_cents: Prix en centimes (pour éviter les erreurs de précision)
        stock_qty: Quantité en stock
        active: Indique si le produit est actuellement disponible à la vente
    """
    id: str
    name: str
    description: str
    price_cents: int
    stock_qty: int
    active: bool = True


@dataclass
class CartItem:
    """
    Représente un article dans le panier d'achat.
    
    Attributes:
        product_id: Référence vers le produit
        quantity: Quantité commandée
    """
    product_id: str
    quantity: int


@dataclass
class Cart:
    """
    Panier d'achat d'un utilisateur.
    
    Attributes:
        user_id: Identifiant de l'utilisateur propriétaire du panier
        items: Dictionnaire des articles (clé: product_id)
    """
    user_id: str
    items: dict[str, CartItem] = field(default_factory=dict)

    def add(self, product: Product, qty: int = 1):
        """
        Ajoute un produit au panier.
        
        Args:
            product: Le produit à ajouter
            qty: Quantité à ajouter
            
        Raises:
            ValueError: Si la quantité est invalide, le produit inactif ou le stock insuffisant
        """
        if qty <= 0:
            raise ValueError("Quantité invalide.")
        if not product.active:
            raise ValueError("Produit inactif.")
        if product.stock_qty < qty:
            raise ValueError("Stock insuffisant.")
        
        if product.id in self.items:
            self.items[product.id].quantity += qty
        else:
            self.items[product.id] = CartItem(product_id=product.id, quantity=qty)

    def remove(self, product_id: str, qty: int = 1):
        """
        Retire un produit du panier.
        
        Args:
            product_id: Identifiant du produit à retirer
            qty: Quantité à retirer (si <= 0, retire complètement l'article)
        """
        if product_id not in self.items:
            return
        
        if qty <= 0:
            del self.items[product_id]
            return
        
        self.items[product_id].quantity -= qty
        if self.items[product_id].quantity <= 0:
            del self.items[product_id]

    def clear(self):
        """Vide complètement le panier."""
        self.items.clear()

    def total_cents(self, product_repo: "ProductRepository") -> int:
        """
        Calcule le total du panier en centimes.
        
        Args:
            product_repo: Repository des produits pour récupérer les prix
            
        Returns:
            Total en centimes
        """
        total = 0
        for it in self.items.values():
            p = product_repo.get(it.product_id)
            if p is None or not p.active:
                continue
            total += p.price_cents * it.quantity
        return total
