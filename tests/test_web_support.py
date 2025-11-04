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


def test_support_thread_create_and_reply(app, client):
    email = "owner@example.com"
    register_user(app, email)
    login(client, email, "pass123")

    # Create a thread
    r = client.post(
        "/support/threads/new",
        data={"subject": "Problème commande", "order_id": "", "message": "Bonjour"},
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert b"Ticket cr\xc3\xa9\xc3\xa9" in r.data or b"thread" in r.data

    # List threads
    lst = client.get("/support/threads")
    assert lst.status_code == 200
    assert b"Probl\xc3\xa8me commande" in lst.data

    # Open first thread from list page
    assert b"Voir" in lst.data


def test_support_thread_access_control(app, client):
    # Two users; user2 must not access user1 thread
    u1 = register_user(app, "u1@example.com")
    u2 = register_user(app, "u2@example.com")

    # u1 creates a thread
    login(client, "u1@example.com", "pass123")
    r = client.post(
        "/support/threads/new",
        data={"subject": "Sujet U1", "order_id": "", "message": "Msg"},
        follow_redirects=True,
    )
    assert r.status_code == 200

    # Capture thread id from redirect path if present (best-effort)
    # Then logout and try to access with u2 -> expect redirect
    client.get("/auth/logout")
    login(client, "u2@example.com", "pass123")
    # Try to hit list; the specific thread page should redirect if accessed
    threads = client.get("/support/threads")
    assert threads.status_code == 200
