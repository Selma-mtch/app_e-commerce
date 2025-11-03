from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.orm import sessionmaker
import uuid

from models.order import Order, OrderItem, OrderStatus
from models.delivery import Delivery
from models.db_models import OrderDB, OrderItemDB, DeliveryDB


class OrderRepositoryDB:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, order: Order):
        with self._session_factory().begin() as s:
            s.add(OrderDB(
                id=order.id,
                user_id=order.user_id,
                status=order.status.name,
                created_at=order.created_at,
                validated_at=order.validated_at,
                paid_at=order.paid_at,
                shipped_at=order.shipped_at,
                delivered_at=order.delivered_at,
                cancelled_at=order.cancelled_at,
                refunded_at=order.refunded_at,
                invoice_id=order.invoice_id,
                payment_id=order.payment_id,
            ))
            for it in order.items:
                s.add(OrderItemDB(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=it.product_id,
                    name=it.name,
                    unit_price_cents=it.unit_price_cents,
                    quantity=it.quantity,
                ))

    def get(self, order_id: str) -> Optional[Order]:
        with self._session_factory() as s:
            r = s.get(OrderDB, order_id)
            if not r:
                return None
            items = s.scalars(select(OrderItemDB).where(OrderItemDB.order_id == r.id)).all()
            delivery = s.scalars(select(DeliveryDB).where(DeliveryDB.order_id == r.id)).first()
            return Order(
                id=r.id,
                user_id=r.user_id,
                items=[OrderItem(product_id=i.product_id, name=i.name, unit_price_cents=i.unit_price_cents, quantity=i.quantity) for i in items],
                status=OrderStatus[r.status],
                created_at=r.created_at,
                validated_at=r.validated_at,
                paid_at=r.paid_at,
                shipped_at=r.shipped_at,
                delivered_at=r.delivered_at,
                cancelled_at=r.cancelled_at,
                refunded_at=r.refunded_at,
                delivery=Delivery(id=delivery.id, order_id=delivery.order_id, carrier=delivery.carrier, tracking_number=delivery.tracking_number, address=delivery.address, status=delivery.status) if delivery else None,
                invoice_id=r.invoice_id,
                payment_id=r.payment_id,
            )

    def list_by_user(self, user_id: str) -> list[Order]:
        with self._session_factory() as s:
            rows = s.scalars(select(OrderDB).where(OrderDB.user_id == user_id)).all()
            result: List[Order] = []
            for r in rows:
                items = s.scalars(select(OrderItemDB).where(OrderItemDB.order_id == r.id)).all()
                delivery = s.scalars(select(DeliveryDB).where(DeliveryDB.order_id == r.id)).first()
                result.append(Order(
                    id=r.id,
                    user_id=r.user_id,
                    items=[OrderItem(product_id=i.product_id, name=i.name, unit_price_cents=i.unit_price_cents, quantity=i.quantity) for i in items],
                    status=OrderStatus[r.status],
                    created_at=r.created_at,
                    validated_at=r.validated_at,
                    paid_at=r.paid_at,
                    shipped_at=r.shipped_at,
                    delivered_at=r.delivered_at,
                    cancelled_at=r.cancelled_at,
                    refunded_at=r.refunded_at,
                    delivery=Delivery(id=delivery.id, order_id=delivery.order_id, carrier=delivery.carrier, tracking_number=delivery.tracking_number, address=delivery.address, status=delivery.status) if delivery else None,
                    invoice_id=r.invoice_id,
                    payment_id=r.payment_id,
                ))
            return result

    def update(self, order: Order):
        with self._session_factory().begin() as s:
            s.execute(
                update(OrderDB)
                .where(OrderDB.id == order.id)
                .values(
                    status=order.status.name,
                    validated_at=order.validated_at,
                    paid_at=order.paid_at,
                    shipped_at=order.shipped_at,
                    delivered_at=order.delivered_at,
                    cancelled_at=order.cancelled_at,
                    refunded_at=order.refunded_at,
                    invoice_id=order.invoice_id,
                    payment_id=order.payment_id,
                )
            )
            # Upsert delivery
            if order.delivery:
                d = order.delivery
                existing = s.scalars(select(DeliveryDB).where(DeliveryDB.order_id == order.id)).first()
                if existing:
                    existing.carrier = d.carrier
                    existing.tracking_number = d.tracking_number
                    existing.address = d.address
                    existing.status = d.status
                else:
                    s.add(DeliveryDB(
                        id=d.id,
                        order_id=order.id,
                        carrier=d.carrier,
                        tracking_number=d.tracking_number,
                        address=d.address,
                        status=d.status,
                    ))

