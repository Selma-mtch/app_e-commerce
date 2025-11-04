import pytest
from ecommerce.models.user import User
from ecommerce.models.product import Product
from ecommerce.repositories.user_repository import UserRepository
from ecommerce.repositories.product_repository import ProductRepository
from ecommerce.services.auth.session_manager import SessionManager
from ecommerce.services.auth.auth_service import AuthService
from ecommerce.services.catalog_service import CatalogService


def test_auth_register():
    """Test l'inscription d'un utilisateur."""
    users = UserRepository()
    sessions = SessionManager()
    auth = AuthService(users, sessions)
    
    user = auth.register(
        email="test@example.com",
        password="password123",
        first_name="Jean",
        last_name="Dupont",
        address="123 Rue Test"
    )
    
    assert user.email == "test@example.com"
    assert user.first_name == "Jean"


def test_auth_register_duplicate_email():
    """Test qu'on ne peut pas s'inscrire deux fois avec le même email."""
    users = UserRepository()
    sessions = SessionManager()
    auth = AuthService(users, sessions)
    
    auth.register(
        email="test@example.com",
        password="password123",
        first_name="Jean",
        last_name="Dupont",
        address="123 Rue Test"
    )
    
    with pytest.raises(ValueError, match="Email déjà utilisé"):
        auth.register(
            email="test@example.com",
            password="autre_password",
            first_name="Pierre",
            last_name="Martin",
            address="456 Rue Test"
        )


def test_auth_login():
    """Test la connexion d'un utilisateur."""
    users = UserRepository()
    sessions = SessionManager()
    auth = AuthService(users, sessions)
    
    auth.register(
        email="test@example.com",
        password="password123",
        first_name="Jean",
        last_name="Dupont",
        address="123 Rue Test"
    )
    
    token = auth.login("test@example.com", "password123")
    assert token is not None
    assert isinstance(token, str)
    
    user_id = sessions.get_user_id(token)
    assert user_id is not None


def test_auth_login_invalid_credentials():
    """Test la connexion avec des identifiants invalides."""
    users = UserRepository()
    sessions = SessionManager()
    auth = AuthService(users, sessions)
    
    auth.register(
        email="test@example.com",
        password="password123",
        first_name="Jean",
        last_name="Dupont",
        address="123 Rue Test"
    )
    
    with pytest.raises(ValueError, match="Identifiants invalides"):
        auth.login("test@example.com", "wrong_password")


def test_catalog_list_active_products():
    """Test le listage des produits actifs."""
    products = ProductRepository()
    catalog = CatalogService(products)
    
    p1 = Product(
        id="prod-1",
        name="T-Shirt",
        description="Test",
        price_cents=1999,
        stock_qty=10,
        active=True
    )
    p2 = Product(
        id="prod-2",
        name="Sweat",
        description="Test",
        price_cents=4999,
        stock_qty=5,
        active=False
    )
    
    products.add(p1)
    products.add(p2)
    
    active_products = catalog.list_products()
    assert len(active_products) == 1
    assert active_products[0].name == "T-Shirt"


def test_checkout_and_pay_flow():
    """Parcours de commande: checkout puis paiement carte."""
    from ecommerce.repositories.cart_repository import CartRepository
    from ecommerce.repositories.order_repository import OrderRepository
    from ecommerce.repositories.invoice_repository import InvoiceRepository
    from ecommerce.repositories.payment_repository import PaymentRepository
    from ecommerce.services.order_service import OrderService
    from ecommerce.services.billing_service import BillingService
    from ecommerce.services.delivery_service import DeliveryService
    from ecommerce.services.payment_gateway import PaymentGateway

    users = UserRepository()
    # Utiliser un user existant du repo en mémoire
    user = users.get("1") or users.get("2")

    products = ProductRepository()
    p1 = Product(id="p1", name="Prod1", description="d", price_cents=1000, stock_qty=5, active=True)
    products.add(p1)

    carts = CartRepository()
    orders = OrderRepository()
    invoices = InvoiceRepository()
    payments = PaymentRepository()
    billing = BillingService(invoices)
    delivery = DeliveryService()
    gateway = PaymentGateway()

    svc = OrderService(orders, products, carts, payments, invoices, billing, delivery, gateway, users)

    # Ajouter au panier et checkout
    carts.get_or_create(user.id).add(p1, 2)
    order = svc.checkout(user.id)
    assert order.status.name == "CREE"
    assert orders.get(order.id) is not None

    # Paiement
    payment = svc.pay_by_card(order.id, "4242424242424242", 12, 2030, "123")
    assert payment.succeeded is True
    order2 = orders.get(order.id)
    assert order2.status.name == "PAYEE"
    assert order2.invoice_id is not None


def test_checkout_rollback_on_reservation_failure():
    """Si une réservation échoue en cours de route, rollback des réservations précédentes."""
    from ecommerce.repositories.cart_repository import CartRepository
    from ecommerce.repositories.order_repository import OrderRepository
    from ecommerce.repositories.invoice_repository import InvoiceRepository
    from ecommerce.repositories.payment_repository import PaymentRepository
    from ecommerce.services.order_service import OrderService
    from ecommerce.services.billing_service import BillingService
    from ecommerce.services.delivery_service import DeliveryService
    from ecommerce.services.payment_gateway import PaymentGateway

    users = UserRepository()
    user = users.get("1") or users.get("2")

    products = ProductRepository()
    p1 = Product(id="p1", name="Prod1", description="d", price_cents=1000, stock_qty=5, active=True)
    p2 = Product(id="p2", name="Prod2", description="d", price_cents=2000, stock_qty=5, active=True)
    products.add(p1)
    products.add(p2)

    carts = CartRepository()
    orders = OrderRepository()
    invoices = InvoiceRepository()
    payments = PaymentRepository()
    billing = BillingService(invoices)
    delivery = DeliveryService()
    gateway = PaymentGateway()

    svc = OrderService(orders, products, carts, payments, invoices, billing, delivery, gateway, users)

    carts.get_or_create(user.id).add(p1, 2)
    carts.get_or_create(user.id).add(p2, 2)

    # Monkeypatch: échec de réservation pour p2 après que p1 a été réservé
    orig_reserve = products.reserve_stock

    def failing_reserve(pid: str, qty: int):
        if pid == p2.id:
            raise ValueError("Stock reservation failure")
        return orig_reserve(pid, qty)

    products.reserve_stock = failing_reserve  # type: ignore

    with pytest.raises(ValueError):
        svc.checkout(user.id)

    # Stock inchangé grâce au rollback
    assert products.get(p1.id).stock_qty == 5
    assert products.get(p2.id).stock_qty == 5
    assert orders.list_by_user(user.id) == []
