import pytest


def make_app_csrf():
    from web.app import create_app
    app = create_app('testing')
    # Laisser CSRF actif pour ce test
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    return app


@pytest.fixture
def app_csrf():
    return make_app_csrf()


@pytest.fixture
def client_csrf(app_csrf):
    return app_csrf.test_client()


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


def test_csrf_error_add_to_cart_redirects_with_flash(app_csrf, client_csrf):
    # User + product
    register_user(app_csrf, "csrf@example.com")
    with app_csrf.app_context():
        from models.product import Product
        p = Product(id="c1", name="CSRF", description="d", price_cents=1000, stock_qty=10, active=True)
        app_csrf.products_repo.add(p)

    login(client_csrf, "csrf@example.com", "pass123")
    # Post without CSRF token
    r = client_csrf.post("/cart/add/c1", headers={"Referer": "/catalog/products"}, follow_redirects=True)
    assert r.status_code == 200
    # The handler flashes a warning; ensure some indicative text is present
    assert b"Session expir\xc3\xa9e" in r.data or b"Veuillez r\xc3\xa9essayer" in r.data
