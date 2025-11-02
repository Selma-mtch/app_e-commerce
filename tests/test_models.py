import pytest
from ecommerce.models.user import User
from ecommerce.models.product import Product, Cart, CartItem
from ecommerce.models.order import Order, OrderItem, OrderStatus


def test_user_creation():
    """Test la création d'un utilisateur."""
    user = User(
        id="user-1",
        email="test@example.com",
        password_hash="hash123",
        first_name="Jean",
        last_name="Dupont",
        address="123 Rue Test",
        is_admin=False
    )
    assert user.email == "test@example.com"
    assert user.is_admin is False


def test_user_update_profile():
    """Test la mise à jour du profil utilisateur."""
    user = User(
        id="user-1",
        email="test@example.com",
        password_hash="hash123",
        first_name="Jean",
        last_name="Dupont",
        address="123 Rue Test"
    )
    
    user.update_profile(first_name="Pierre", address="456 Rue Nouvelle")
    assert user.first_name == "Pierre"
    assert user.address == "456 Rue Nouvelle"
    
    # Les champs protégés ne doivent pas être modifiables
    user.update_profile(email="new@example.com", is_admin=True)
    assert user.email == "test@example.com"
    assert user.is_admin is False


def test_product_creation():
    """Test la création d'un produit."""
    product = Product(
        id="prod-1",
        name="T-Shirt",
        description="Un beau t-shirt",
        price_cents=1999,
        stock_qty=100,
        active=True
    )
    assert product.name == "T-Shirt"
    assert product.price_cents == 1999
    assert product.stock_qty == 100


def test_cart_add_product():
    """Test l'ajout d'un produit au panier."""
    product = Product(
        id="prod-1",
        name="T-Shirt",
        description="Test",
        price_cents=1999,
        stock_qty=10,
        active=True
    )
    
    cart = Cart(user_id="user-1")
    cart.add(product, 2)
    
    assert len(cart.items) == 1
    assert cart.items["prod-1"].quantity == 2
    
    # Ajouter à nouveau
    cart.add(product, 1)
    assert cart.items["prod-1"].quantity == 3


def test_cart_add_inactive_product():
    """Test qu'on ne peut pas ajouter un produit inactif."""
    product = Product(
        id="prod-1",
        name="T-Shirt",
        description="Test",
        price_cents=1999,
        stock_qty=10,
        active=False
    )
    
    cart = Cart(user_id="user-1")
    
    with pytest.raises(ValueError, match="Produit inactif"):
        cart.add(product, 1)


def test_cart_insufficient_stock():
    """Test qu'on ne peut pas ajouter plus que le stock disponible."""
    product = Product(
        id="prod-1",
        name="T-Shirt",
        description="Test",
        price_cents=1999,
        stock_qty=5,
        active=True
    )
    
    cart = Cart(user_id="user-1")
    
    with pytest.raises(ValueError, match="Stock insuffisant"):
        cart.add(product, 10)


def test_order_total():
    """Test le calcul du total d'une commande."""
    items = [
        OrderItem(
            product_id="prod-1",
            name="T-Shirt",
            unit_price_cents=1999,
            quantity=2
        ),
        OrderItem(
            product_id="prod-2",
            name="Sweat",
            unit_price_cents=4999,
            quantity=1
        )
    ]
    
    order = Order(
        id="order-1",
        user_id="user-1",
        items=items,
        status=OrderStatus.CREE,
        created_at=1234567890.0
    )
    
    assert order.total_cents() == (1999 * 2 + 4999 * 1)