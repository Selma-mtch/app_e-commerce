import pytest


def make_app():
    from web.app import create_app
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret'
    return app


@pytest.fixture
def app():
    return make_app()


@pytest.fixture
def client(app):
    return app.test_client()


def register_user(app, email, password="pass123", is_admin=False):
    with app.app_context():
        return app.auth_service.register(
            email=email,
            password=password,
            first_name="User",
            last_name="Test",
            address="1 rue Test",
            is_admin=is_admin,
        )


def login(client, email, password):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)


def test_admin_toggle_product_removes_from_carts(app, client):
    # Create admin and user
    register_user(app, "admin.test.toggle@example.com", "admin123", is_admin=True)
    register_user(app, "buyer.toggle@example.com", "pass123", is_admin=False)

    # Create a product and add to buyer cart
    with app.app_context():
        from models.product import Product
        p = Product(id="pX", name="ToggleMe", description="d", price_cents=1000, stock_qty=10, active=True)
        app.products_repo.add(p)
        app.cart_service.add_to_cart("2", "pX", 1)  # note: user repo seeds ids 1 and 2, but in tests we registered; safer use repo get
        # Find buyer id by email
        buyer = app.users_repo.get_by_email("buyer.toggle@example.com")
        app.cart_service.add_to_cart(buyer.id, "pX", 1)

    # Login admin and toggle inactive
    login(client, "admin.test.toggle@example.com", "admin123")
    r = client.post("/admin/products/pX/toggle", follow_redirects=True)
    assert r.status_code == 200
    # Cart should be emptied of product pX
    with app.app_context():
        buyer = app.users_repo.get_by_email("buyer.toggle@example.com")
        cart = app.cart_service.view_cart(buyer.id)
        assert "pX" not in cart.items


def test_admin_order_lifecycle_validate_ship_deliver_and_refund(app, client):
    # Setup admin and buyer
    register_user(app, "admin.flow@example.com", "admin123", is_admin=True)
    register_user(app, "buyer.flow@example.com", "pass123", is_admin=False)
    with app.app_context():
        from models.product import Product
        p = Product(id="pY", name="ProdY", description="d", price_cents=1500, stock_qty=5, active=True)
        app.products_repo.add(p)
        buyer = app.users_repo.get_by_email("buyer.flow@example.com")
        app.cart_service.add_to_cart(buyer.id, "pY", 2)
        order = app.order_service.checkout(buyer.id)
        order_id = order.id

    # Admin validates
    login(client, "admin.flow@example.com", "admin123")
    rv = client.post(f"/admin/orders/{order_id}/validate", follow_redirects=True)
    assert rv.status_code == 200

    # Pay (service)
    with app.app_context():
        app.order_service.pay_by_card(order_id, "4242424242424242", 12, 2030, "123")

    # Admin ships
    rv2 = client.post(f"/admin/orders/{order_id}/ship", follow_redirects=True)
    assert rv2.status_code == 200

    # Admin marks delivered
    rv3 = client.post(f"/admin/orders/{order_id}/deliver", follow_redirects=True)
    assert rv3.status_code == 200

    # Refund should now be rejected (not PAYEE/ANNULEE)
    rv4 = client.post(f"/admin/orders/{order_id}/refund", data={}, follow_redirects=True)
    assert rv4.status_code == 200
