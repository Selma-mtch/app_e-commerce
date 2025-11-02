from ast import List
from models.product import Product
from repositories.product_repository import ProductRepository


class CatalogService:
    """
    Service de gestion du catalogue produits.
    """
    
    def __init__(self, products: ProductRepository):
        self.products = products

    def list_products(self) -> list[Product]:
        """Liste tous les produits actifs du catalogue."""
        return self.products.list_active()