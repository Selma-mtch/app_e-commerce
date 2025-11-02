from ast import Dict, List
from typing import Optional

from models.product import Product


class ProductRepository:
    """
    Gère le catalogue de produits et les stocks.
    """
    
    def __init__(self):
        self._by_id: Dict[str, Product] = {}

    def add(self, product: Product):
        """Ajoute un produit au catalogue."""
        self._by_id[product.id] = product

    def get(self, product_id: str) -> Optional[Product]:
        """Récupère un produit par son ID."""
        return self._by_id.get(product_id)

    def list_active(self) -> list[Product]:
        """Liste tous les produits actifs."""
        return [p for p in self._by_id.values() if p.active]

    def reserve_stock(self, product_id: str, qty: int):
        """
        Réserve une quantité de stock pour un produit.
        
        Args:
            product_id: ID du produit
            qty: Quantité à réserver
            
        Raises:
            ValueError: Si le stock est insuffisant
        """
        p = self.get(product_id)
        if not p or p.stock_qty < qty:
            raise ValueError("Stock insuffisant.")
        p.stock_qty -= qty

    def release_stock(self, product_id: str, qty: int):
        """
        Libère une quantité de stock (annulation/remboursement).
        
        Args:
            product_id: ID du produit
            qty: Quantité à libérer
        """
        p = self.get(product_id)
        if p:
             p.stock_qty += qty

  