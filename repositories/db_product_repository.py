from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from models.product import Product
from models.db_models import ProductDB


class ProductRepositoryDB:
    """Dépôt de produits basé sur SQLAlchemy.

    Fournit l'API produits (création/lecture/liste) et la gestion de stock
    transactionnelle (réservation/libération).
    """

    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, product: Product):
        """Crée ou met à jour un produit (upsert simple)."""
        with self._session_factory() as s:  # type: Session
            obj = s.get(ProductDB, product.id)
            if obj:
                obj.name = product.name
                obj.description = product.description
                obj.price_cents = product.price_cents
                obj.stock_qty = product.stock_qty
                obj.active = product.active
            else:
                obj = ProductDB(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price_cents=product.price_cents,
                    stock_qty=product.stock_qty,
                    active=product.active,
                )
                s.add(obj)
            s.commit()

    def get(self, product_id: str) -> Optional[Product]:
        """Retourne un produit par son identifiant ou ``None`` s'il n'existe pas."""
        with self._session_factory() as s:
            row = s.get(ProductDB, product_id)
            if not row:
                return None
            return Product(
                id=row.id,
                name=row.name,
                description=row.description,
                price_cents=row.price_cents,
                stock_qty=row.stock_qty,
                active=row.active,
            )

    def list_active(self) -> list[Product]:
        """Liste uniquement les produits actifs."""
        with self._session_factory() as s:
            rows = s.scalars(select(ProductDB).where(ProductDB.active == True)).all()  # noqa: E712
            return [
                Product(
                    id=r.id,
                    name=r.name,
                    description=r.description,
                    price_cents=r.price_cents,
                    stock_qty=r.stock_qty,
                    active=r.active,
                )
                for r in rows
            ]

    def list_all(self) -> list[Product]:
        """Liste tous les produits, actifs et inactifs."""
        with self._session_factory() as s:
            rows = s.scalars(select(ProductDB)).all()
            return [
                Product(
                    id=r.id,
                    name=r.name,
                    description=r.description,
                    price_cents=r.price_cents,
                    stock_qty=r.stock_qty,
                    active=r.active,
                )
                for r in rows
            ]

    def reserve_stock(self, product_id: str, qty: int):
        """Décrémente le stock si disponible, sinon lève ``ValueError``."""
        with self._session_factory.begin() as s:
            res = s.execute(
                update(ProductDB)
                .where(ProductDB.id == product_id)
                .where(ProductDB.stock_qty >= qty)
                .values(stock_qty=ProductDB.stock_qty - qty)
            )
            if res.rowcount == 0:
                raise ValueError("Stock insuffisant.")

    def release_stock(self, product_id: str, qty: int):
        """Ré‑augmente le stock (annulation/remboursement)."""
        with self._session_factory.begin() as s:
            s.execute(
                update(ProductDB)
                .where(ProductDB.id == product_id)
                .values(stock_qty=ProductDB.stock_qty + qty)
            )
"""Dépôt SQLAlchemy des produits et gestion transactionnelle du stock."""
