from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import sessionmaker

from models.product import Cart, CartItem
from models.db_models import CartItemDB


class CartRepositoryDB:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_or_create(self, user_id: str) -> Cart:
        with self._session_factory() as s:
            rows = s.scalars(select(CartItemDB).where(CartItemDB.user_id == user_id)).all()
            items = {r.product_id: CartItem(product_id=r.product_id, quantity=r.quantity) for r in rows}
            return Cart(user_id=user_id, items=items)

    def clear(self, user_id: str):
        with self._session_factory().begin() as s:
            s.execute(delete(CartItemDB).where(CartItemDB.user_id == user_id))

    def add_item(self, user_id: str, product_id: str, qty: int = 1):
        if qty <= 0:
            return
        with self._session_factory().begin() as s:
            # UPSERT-like: try update, if nothing updated, insert
            res = s.execute(
                update(CartItemDB)
                .where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id)
                .values(quantity=CartItemDB.quantity + qty)
            )
            if res.rowcount == 0:
                s.add(CartItemDB(user_id=user_id, product_id=product_id, quantity=qty))

    def remove_item(self, user_id: str, product_id: str, qty: int = 1):
        with self._session_factory().begin() as s:
            if qty <= 0:
                s.execute(delete(CartItemDB).where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id))
                return
            # decrement and delete if <= 0
            res = s.execute(
                update(CartItemDB)
                .where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id)
                .values(quantity=CartItemDB.quantity - qty)
            )
            # Cleanup negatives
            s.execute(delete(CartItemDB).where(CartItemDB.user_id == user_id, CartItemDB.product_id == product_id, CartItemDB.quantity <= 0))

    def remove_product_everywhere(self, product_id: str) -> int:
        with self._session_factory().begin() as s:
            res = s.execute(delete(CartItemDB).where(CartItemDB.product_id == product_id))
            return res.rowcount or 0

