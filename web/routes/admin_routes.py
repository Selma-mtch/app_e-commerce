"""Routes backoffice admin."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from web.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Tableau de bord admin avec indicateurs clés."""
    users_count = len(getattr(current_app.users_repo, '_by_id', {}))
    products_count = len(getattr(current_app.products_repo, '_by_id', {}))
    orders_count = len(getattr(current_app.orders_repo, '_by_id', {}))
    invoices_count = len(getattr(current_app.invoices_repo, '_by_id', {}))
    payments_count = len(getattr(current_app.payments_repo, '_by_id', {}))
    threads_count = len(getattr(current_app.threads_repo, '_by_id', {}))
    return render_template(
        'admin/dashboard.html',
        users_count=users_count,
        products_count=products_count,
        orders_count=orders_count,
        invoices_count=invoices_count,
        payments_count=payments_count,
        threads_count=threads_count,
    )


@admin_bp.route('/orders')
@admin_required
def orders():
    """Liste de toutes les commandes et actions possibles."""
    all_orders = []
    for user_id in getattr(current_app.orders_repo, '_by_user', {}).keys():
        all_orders.extend(current_app.orders_repo.list_by_user(user_id))
    return render_template('admin/orders.html', orders=all_orders)


@admin_bp.route('/orders/<order_id>/validate', methods=['POST'])
@admin_required
def validate_order(order_id):
    """Valider une commande (statut -> VALIDEE)."""
    try:
        current_app.order_service.backoffice_validate_order(session['user_id'], order_id)
        flash('Commande validée.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/<order_id>/ship', methods=['POST'])
@admin_required
def ship_order(order_id):
    """Expédier une commande (statut -> EXPEDIEE)."""
    try:
        current_app.order_service.backoffice_ship_order(session['user_id'], order_id)
        flash('Commande expédiée.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/<order_id>/deliver', methods=['POST'])
@admin_required
def mark_delivered(order_id):
    """Marquer une commande livrée (statut -> LIVREE)."""
    try:
        current_app.order_service.backoffice_mark_delivered(session['user_id'], order_id)
        flash('Commande marquée livrée.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/<order_id>/refund', methods=['POST'])
@admin_required
def refund_order(order_id):
    """Rembourser une commande (partiel ou total)."""
    amount = request.form.get('amount_cents')
    amount_cents = int(amount) if amount and amount.isdigit() else None
    try:
        current_app.order_service.backoffice_refund(session['user_id'], order_id, amount_cents)
        flash('Commande remboursée.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.orders'))


@admin_bp.route('/products')
@admin_required
def products():
    """Catalogue produits (admin)."""
    products = list(getattr(current_app.products_repo, '_by_id', {}).values())
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/<product_id>/toggle', methods=['POST'])
@admin_required
def toggle_product(product_id):
    """Active/désactive un produit."""
    p = current_app.products_repo.get(product_id)
    if not p:
        flash('Produit introuvable.', 'danger')
        return redirect(url_for('admin.products'))
    p.active = not p.active
    # Persister l'état actif/inactif en base si repo DB
    try:
        current_app.products_repo.add(p)  # no-op for memory, upsert for DB
    except Exception:
        pass
    if not p.active:
        # Retirer le produit de tous les paniers
        affected = current_app.carts_repo.remove_product_everywhere(product_id)
        flash((f'Produit désactivé et retiré de {affected} panier(s).' if affected else 'Produit désactivé.'), 'info')
    else:
        flash('Produit activé.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/support')
@admin_required
def support():
    """Liste des tickets support (admin)."""
    threads = list(getattr(current_app.threads_repo, '_by_id', {}).values())
    return render_template('admin/support.html', threads=threads)


@admin_bp.route('/support/<thread_id>/close', methods=['POST'])
@admin_required
def close_thread(thread_id):
    """Ferme un ticket support."""
    try:
        current_app.customer_service.close_thread(thread_id, session['user_id'])
        flash('Ticket fermé.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.support'))


@admin_bp.route('/support/<thread_id>', methods=['GET', 'POST'])
@admin_required
def support_thread(thread_id):
    """Détail d'un ticket côté admin, avec réponse agent."""
    thread = current_app.customer_service.get_thread(thread_id)
    if not thread:
        flash('Ticket introuvable.', 'danger')
        return redirect(url_for('admin.support'))
    if request.method == 'POST':
        try:
            body = request.form['message']
            # Réponse agent: author_user_id=None
            current_app.customer_service.post_message(thread_id=thread.id, author_user_id=None, body=body)
            flash('Réponse envoyée.', 'success')
            return redirect(url_for('admin.support_thread', thread_id=thread.id))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('admin/support_thread.html', thread=thread)
