"""Application Flask principale."""

from flask import Flask, render_template, session, current_app
from flask_login import LoginManager
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
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialiser les services
    init_services(app)
    
    # Charger les données de démo
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
    return app
