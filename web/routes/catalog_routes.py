"""Routes du catalogue produits."""

from flask import Blueprint, render_template, current_app

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')


@catalog_bp.route('/products')
def products():
    """Liste des produits."""
    products = current_app.catalog_service.list_products()
    return render_template('catalog/products.html', products=products)
