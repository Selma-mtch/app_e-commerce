import os
import pytest


def make_app_db(tmp_path):
    # Utilise une base SQLite fichier pour simuler le mode prod (repos DB)
    db_path = tmp_path / "auth_db.sqlite"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    from web.app import create_app
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret'
    return app


@pytest.fixture
def app_db(tmp_path, monkeypatch):
    # S'assurer que toute autre URL DB est neutralisée puis définie pour ce test
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = make_app_db(tmp_path)
    yield app
    # Nettoyage implicite par tmp_path


@pytest.fixture
def client_db(app_db):
    return app_db.test_client()


def register_user_db(app_db, email="dbuser@example.com", password="pass123", is_admin=False):
    with app_db.app_context():
        return app_db.auth_service.register(
            email=email,
            password=password,
            first_name="Jean",
            last_name="DB",
            address="1 rue DB",
            is_admin=is_admin,
        )


def login_db(client_db, email, password):
    return client_db.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_account_change_email_and_password_db(app_db, client_db):
    email = "produser@example.com"
    register_user_db(app_db, email=email)

    # Login initial
    r = login_db(client_db, email, "pass123")
    assert r.status_code == 200

    # Changer l'email (vérif DB persistance)
    r2 = client_db.post(
        "/auth/account",
        data={
            "action": "change_email",
            "new_email": "produser.new@example.com",
            "current_password": "pass123",
        },
        follow_redirects=True,
    )
    assert r2.status_code == 200

    # Déconnexion puis login avec le nouvel email (doit lire depuis DB)
    client_db.get("/auth/logout")
    r3 = login_db(client_db, "produser.new@example.com", "pass123")
    assert r3.status_code == 200

    # Changer le mot de passe
    r4 = client_db.post(
        "/auth/account",
        data={
            "action": "change_password",
            "current_password": "pass123",
            "new_password": "newpasswordDB",
            "confirm_password": "newpasswordDB",
        },
        follow_redirects=True,
    )
    assert r4.status_code == 200

    # Ancien mot de passe invalide, nouveau OK
    client_db.get("/auth/logout")
    fail = client_db.post(
        "/auth/login",
        data={"email": "produser.new@example.com", "password": "pass123"},
        follow_redirects=False,
    )
    assert fail.status_code in (200, 302, 303)
    ok = login_db(client_db, "produser.new@example.com", "newpasswordDB")
    assert ok.status_code == 200

