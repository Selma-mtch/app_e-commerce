"""Routes du catalogue produits."""

from flask import Blueprint, render_template, current_app, flash, redirect, url_for
from flask_login import current_user

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')


@catalog_bp.route('/products')
def products():
    """Liste des produits."""
    if current_user.is_authenticated and current_user.is_admin:
        # Les admins voient tous les produits (y compris désactivés)
        products = list(getattr(current_app.products_repo, '_by_id', {}).values())
    else:
        products = current_app.catalog_service.list_products()
    return render_template('catalog/products.html', products=products)


@catalog_bp.route('/products/<product_id>')
def product_detail(product_id: str):
    """Détail d'un produit."""
    product = current_app.products_repo.get(product_id)
    if not product:
        flash('Produit introuvable.', 'danger')
        return redirect(url_for('catalog.products'))
    # Autoriser l'accès aux admins même si désactivé
    if (not product.active) and not (current_user.is_authenticated and current_user.is_admin):
        flash('Produit introuvable.', 'danger')
        return redirect(url_for('catalog.products'))
    return render_template('product.html', product=product)
