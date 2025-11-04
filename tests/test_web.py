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


def register_user(app, email="testuser@example.com", password="pass123", is_admin=False):
    with app.app_context():
        # Utiliser le service directement pour pouvoir créer un admin si besoin
        return app.auth_service.register(
            email=email,
            password=password,
            first_name="Jean",
            last_name="Dupont",
            address="1 rue Test",
            is_admin=is_admin,
        )


def login(client, email, password):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_auth_register_login_and_navbar(app, client):
    email = "testuser@example.com"
    register_user(app, email=email)
    r = login(client, email, "pass123")
    assert r.status_code == 200
    # La navbar doit afficher le lien vers le compte utilisateur
    home = client.get("/")
    assert home.status_code == 200
    assert email.encode() in home.data


def test_catalog_search_filters_results(app, client):
    # Créer quelques produits dans le repo en mémoire
    with app.app_context():
        from models.product import Product
        import uuid
        app.products_repo.add(Product(id=str(uuid.uuid4()), name="T-Shirt", description="coton", price_cents=1500, stock_qty=10))
        app.products_repo.add(Product(id=str(uuid.uuid4()), name="Sweat", description="molleton chaud", price_cents=4000, stock_qty=5))

    r = client.get("/catalog/products?q=sweat")
    assert r.status_code == 200
    assert b"Sweat" in r.data
    assert b"T-Shirt" not in r.data


def test_cart_add_requires_login(app, client):
    # Produit d'essai
    with app.app_context():
        from models.product import Product
        pid = "p1"
        app.products_repo.add(Product(id=pid, name="Prod1", description="d", price_cents=1000, stock_qty=5))

    r = client.post(f"/cart/add/{pid}")
    # Redirigé vers la page de login
    assert r.status_code in (302, 303)
    assert "/auth/login" in r.headers.get("Location", "")


def test_cart_add_after_login(app, client):
    # Setup: user + produit
    email = "buyer@example.com"
    register_user(app, email=email)
    with app.app_context():
        from models.product import Product
        pid = "p2"
        app.products_repo.add(Product(id=pid, name="Prod2", description="d", price_cents=1000, stock_qty=5))

    login(client, email, "pass123")
    r = client.post(f"/cart/add/{pid}", follow_redirects=True)
    assert r.status_code == 200
    # La page panier doit contenir le produit après ajout
    cart = client.get("/cart/", follow_redirects=True)
    assert cart.status_code == 200
    assert b"Prod2" in cart.data
