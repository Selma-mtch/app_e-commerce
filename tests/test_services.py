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