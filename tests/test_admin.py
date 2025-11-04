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


def register_user(app, email, password, is_admin=False):
    with app.app_context():
        return app.auth_service.register(
            email=email,
            password=password,
            first_name="Admin" if is_admin else "User",
            last_name="Test",
            address="1 rue Test",
            is_admin=is_admin,
        )


def login(client, email, password):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)


def test_admin_products_requires_admin(app, client):
    # Sans login -> redirection login
    r = client.get("/admin/products")
    assert r.status_code in (302, 303)
    assert "/auth/login" in r.headers.get("Location", "")

    # Avec utilisateur non-admin -> redirection catalogue
    register_user(app, "user2@example.com", "pass123", is_admin=False)
    login(client, "user2@example.com", "pass123")
    r2 = client.get("/admin/products")
    assert r2.status_code in (302, 303)
    assert "/catalog/products" in r2.headers.get("Location", "")


def test_admin_can_create_product(app, client):
    # Login admin
    register_user(app, "admin2@example.com", "admin123", is_admin=True)
    login(client, "admin2@example.com", "admin123")

    # Créer un produit
    r = client.post(
        "/admin/products/new",
        data={
            "name": "Chaussures",
            "description": "Confortables",
            "price_eur": "59.90",
            "stock_qty": "12",
            "active": "on",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert b"Produit cr\xc3\xa9\xc3\xa9 avec succ\xc3\a8s" in r.data or b"Produits" in r.data

    # Le produit doit appara\xc3\xaitre dans le catalogue public
    cat = client.get("/catalog/products")
    assert cat.status_code == 200
    assert b"Chaussures" in cat.data
