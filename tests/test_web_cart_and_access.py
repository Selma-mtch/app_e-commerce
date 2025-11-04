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


def test_htmx_add_updates_cart_count(app, client):
    register_user(app, "hx@example.com")
    with app.app_context():
        from models.product import Product
        p = Product(id="hx1", name="HX", description="d", price_cents=1000, stock_qty=10, active=True)
        app.products_repo.add(p)

    login(client, "hx@example.com", "pass123")
    r = client.post(
        "/cart/add/hx1",
        headers={"HX-Request": "true"},
        data={"quantity": "1"},
    )
    assert r.status_code == 200
    assert b"id=\"cart-count\"" in r.data


def test_inactive_product_access_control(app, client):
    # Create product inactive
    with app.app_context():
        from models.product import Product
        p = Product(id="inact1", name="OFF", description="d", price_cents=1000, stock_qty=10, active=False)
        app.products_repo.add(p)

    # Non admin should be redirected to catalog
    register_user(app, "user.inactive@example.com")
    login(client, "user.inactive@example.com", "pass123")
    resp = client.get("/catalog/products/inact1", follow_redirects=False)
    assert resp.status_code in (302, 303)

    # Admin can view
    client.get("/auth/logout")
    register_user(app, "admin.inactive@example.com", "admin123", is_admin=True)
    login(client, "admin.inactive@example.com", "admin123")
    ok = client.get("/catalog/products/inact1")
    assert ok.status_code == 200
