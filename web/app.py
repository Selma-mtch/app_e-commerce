"""Application Flask principale."""

import logging
import os
from flask import Flask, render_template, session, current_app, request
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
from config import config
from datetime import datetime

from models.user import User  

# Import des services (singleton pattern)
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from repositories.cart_repository import CartRepository
from repositories.order_repository import OrderRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.payment_repository import PaymentRepository
from repositories.thread_repository import ThreadRepository
from repositories.db_product_repository import ProductRepositoryDB
from repositories.db_user_repository import UserRepositoryDB
from repositories.db_order_repository import OrderRepositoryDB
from repositories.db_payment_repository import PaymentRepositoryDB
from repositories.db_invoice_repository import InvoiceRepositoryDB
from repositories.db_thread_repository import ThreadRepositoryDB
from repositories.db_cart_repository import CartRepositoryDB
from db.core import build_engine_from_env, Base

from services.auth.session_manager import SessionManager
from services.auth.auth_service import AuthService
from services.catalog_service import CatalogService
from services.cart_service import CartService
from services.order_service import OrderService
from services.billing_service import BillingService
from services.delivery_service import DeliveryService
from services.payment_gateway import PaymentGateway
from services.customer_service import CustomerService

# Initialisation Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login" # redirige vers la page de login si pas connecté

def init_services(app):
    """Initialise les services et les attache à l'application."""
    # Repositories
    if getattr(app, 'db_sessionmaker', None):
        sf = app.db_sessionmaker
        app.users_repo = UserRepositoryDB(sf)
        app.products_repo = ProductRepositoryDB(sf)
        app.carts_repo = CartRepositoryDB(sf)
        app.orders_repo = OrderRepositoryDB(sf)
        app.invoices_repo = InvoiceRepositoryDB(sf)
        app.payments_repo = PaymentRepositoryDB(sf)
        app.threads_repo = ThreadRepositoryDB(sf)
    else:
        app.users_repo = UserRepository()
        app.products_repo = ProductRepository()
        app.carts_repo = CartRepository()
        app.orders_repo = OrderRepository()
        app.invoices_repo = InvoiceRepository()
        app.payments_repo = PaymentRepository()
        app.threads_repo = ThreadRepository()
    
    # Services
    app.sessions = SessionManager()
    app.auth_service = AuthService(app.users_repo, app.sessions)
    app.catalog_service = CatalogService(app.products_repo)
    app.cart_service = CartService(app.carts_repo, app.products_repo)
    app.billing_service = BillingService(app.invoices_repo)
    app.delivery_service = DeliveryService()
    app.payment_gateway = PaymentGateway()
    app.order_service = OrderService(
        app.orders_repo,
        app.products_repo,
        app.carts_repo,
        app.payments_repo,
        app.invoices_repo,
        app.billing_service,
        app.delivery_service,
        app.payment_gateway,
        app.users_repo
    )
    app.customer_service = CustomerService(app.threads_repo, app.users_repo)


def init_sample_data(app):
    """Charge des données de démonstration."""
    from models.product import Product
    import uuid
    
    # Produits de démo
    products = [
        Product(
            id=str(uuid.uuid4()),
            name="T-Shirt Logo",
            description="T-shirt en coton bio avec logo",
            price_cents=1999,
            stock_qty=100
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Sweat à Capuche",
            description="Sweat confortable en molleton",
            price_cents=4999,
            stock_qty=50
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Jean Slim",
            description="Jean stretch confortable",
            price_cents=7999,
            stock_qty=30
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Casquette",
            description="Casquette ajustable",
            price_cents=1499,
            stock_qty=75
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Chaussettes (x3)",
            description="Lot de 3 paires de chaussettes",
            price_cents=899,
            stock_qty=200
        )
    ]
    
    for p in products:
        app.products_repo.add(p)
    
    # Utilisateur admin de démo
    try:
        app.auth_service.register(
            email="admin@shop.local",
            password="admin",
            first_name="Admin",
            last_name="Shop",
            address="1 Rue du Commerce",
            is_admin=True
        )
    except ValueError:
        pass  # L'admin existe déjà


def create_app(config_name='default'):
    """
    Factory pour créer l'application Flask.
    
    Args:
        config_name: Nom de la configuration à utiliser
        
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__, static_folder='templates/static', static_url_path='/static')
    app.config.from_object(config[config_name])
    
    # Logging de base
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    # Sécurité: clé secrète obligatoire en production (pas en mode test)
    if (
        not app.config.get('DEBUG')
        and not app.config.get('TESTING')
        and (
            not app.config.get('SECRET_KEY')
            or app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production'
        )
    ):
        raise RuntimeError('SECRET_KEY must be set in production')
    
    # Protection CSRF
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Base de données (si DATABASE_URL défini)
    db_pair = build_engine_from_env()
    if db_pair:
        engine, SessionLocal = db_pair
        app.db_engine = engine
        app.db_sessionmaker = SessionLocal
        if app.config.get('DB_AUTO_CREATE', False):
            Base.metadata.create_all(engine)
        logging.info("Database initialised.")
    else:
        app.db_engine = None
        app.db_sessionmaker = None

    # Initialiser les services
    init_services(app)
    
    # Charger les données de démo (désactivable par config)
    if app.config.get('LOAD_SAMPLE_DATA', True):
        init_sample_data(app)

    #Initialisation Flask-Login
    login_manager.init_app(app)

    # Exemple de modèle User minimal
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return app.users_repo.get(user_id)
    
    # Enregistrer les blueprints (routes)
    from web.routes.auth_routes import auth_bp
    from web.routes.catalog_routes import catalog_bp
    from web.routes.cart_routes import cart_bp
    from web.routes.order_routes import order_bp
    from web.routes.admin_routes import admin_bp
    from web.routes.support_routes import support_bp
    from web.routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(user_bp)
    
    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        """Convertit un timestamp en format lisible DD/MM/YYYY HH:MM"""
    
        return datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M')

    # Route d'accueil
    @app.route('/')
    def index():
        cart = session.get('cart', [])
        return render_template('index.html', cart=cart)
    
    @app.context_processor
    def inject_user_and_cart():
        cart_count = 0
        if 'user_id' in session:
            cart = current_app.cart_service.view_cart(session['user_id'])
            cart_count = sum(item.quantity for item in cart.items.values())
        return {'cart_count': cart_count}

    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': lambda: generate_csrf()}

    @app.after_request
    def add_no_cache_headers(response):
        """Empêche la mise en cache des pages vues en étant connecté.

        Évite que le bouton "Retour" affiche une page authentifiée après déconnexion.
        Conserve le cache pour les assets statiques.
        """
        if request.endpoint == 'static':
            return response
        if current_user.is_authenticated or 'user_id' in session:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Vary'] = 'Cookie'
        return response

    # Gestion d'erreurs simples
    @app.errorhandler(404)
    def not_found(e):
        return render_template('index.html'), 404

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('index.html'), 400

    @app.errorhandler(500)
    def server_error(e):
        return render_template('index.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Gère proprement les erreurs CSRF.

        Cas courant: la page catalogue a été rendue avant connexion, le token CSRF
        est donc périmé après login. On affiche un message et on redirige vers la
        page précédente (ou le catalogue) pour régénérer un token valide.
        """
        flash('Session expirée ou formulaire périmé. Veuillez réessayer.', 'warning')
        return redirect(request.referrer or url_for('catalog.products'))
    return app
