from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import sessionmaker

from models.product import Cart, CartItem
from models.db_models import CartItemDB


class CartRepositoryDB:
    """Dépôt panier basé sur SQLAlchemy.

    Fournit des opérations de lecture/écriture des items de panier pour un
    utilisateur, avec transactions atomiques.
    """
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_or_create(self, user_id: str) -> Cart:
        """Récupère le panier de l'utilisateur, ou un panier vide s'il n'existe pas."""
        with self._session_factory() as s:
            rows = s.scalars(select(CartItemDB).where(CartItemDB.user_id == user_id)).all()
            items = {r.product_id: CartItem(product_id=r.product_id, quantity=r.quantity) for r in rows}
            return Cart(user_id=user_id, items=items)

    def clear(self, user_id: str):
        # Utiliser sessionmaker.begin() pour obtenir une Session avec transaction
        with self._session_factory.begin() as s:
            s.execute(delete(CartItemDB).where(CartItemDB.user_id == user_id))

    def add_item(self, user_id: str, product_id: str, qty: int = 1):
        """Ajoute une quantité au panier (UPSERT). Ignore si ``qty<=0``."""
        if qty <= 0:
            return
        with self._session_factory.begin() as s:
            # À la manière d'un UPSERT : tenter une mise à jour, sinon insérer
            res = s.execute(
                update(CartItemDB)
                .where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id)
                .values(quantity=CartItemDB.quantity + qty)
            )
            if res.rowcount == 0:
                s.add(CartItemDB(user_id=user_id, product_id=product_id, quantity=qty))

    def remove_item(self, user_id: str, product_id: str, qty: int = 1):
        """Retire une quantité ou supprime la ligne si ``qty<=0`` ou résultat ≤ 0."""
        with self._session_factory.begin() as s:
            if qty <= 0:
                s.execute(delete(CartItemDB).where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id))
                return
            # Décrémenter et supprimer si <= 0
            res = s.execute(
                update(CartItemDB)
                .where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id)
                .values(quantity=CartItemDB.quantity - qty)
            )
            # Nettoyage des valeurs négatives
            s.execute(delete(CartItemDB).where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id, CartItemDB.quantity <= 0))

    def set_quantity(self, user_id: str, product_id: str, qty: int) -> None:
        """Fixe directement la quantité pour un item de panier (UPSERT ou suppression)."""
        with self._session_factory.begin() as s:
            if qty <= 0:
                s.execute(
                    delete(CartItemDB).where(
                        CartItemDB.user_id == user_id,
                        CartItemDB.product_id == product_id,
                    )
                )
                return

            res = s.execute(
                update(CartItemDB)
                .where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id)
                .values(quantity=qty)
            )
            if res.rowcount == 0:
                s.add(CartItemDB(user_id=user_id, product_id=product_id, quantity=qty))

    def remove_product_everywhere(self, product_id: str) -> int:
        """Retire un produit de tous les paniers. Retourne le nombre de paniers affectés."""
        with self._session_factory.begin() as s:
            res = s.execute(delete(CartItemDB).where(CartItemDB.product_id == product_id))
            return res.rowcount or 0
"""Dépôt SQLAlchemy pour la gestion des paniers (lecture/écriture des items)."""
