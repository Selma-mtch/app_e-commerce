"""Routes backoffice admin."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from web.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Tableau de bord admin."""
    return render_template('admin/dashboard.html')


@admin_bp.route('/orders')
@admin_required
def orders():
    """Liste de toutes les commandes."""
    all_orders = []
    for user_id in current_app.orders_repo._by_user.keys():
        all_orders.extend(current_app.orders_repo.list_by_user(user_id))
    
    return render_template('admin/orders.html', orders=all_orders)


@admin_bp.route('/orders/<order_id>/validate', methods=['POST'])
@admin_required
def validate_order(order_id):
    """Valider une commande."""
    try:
        current_app.order_service.backoffice_validate_order(session['user_id'], order_id)
        flash('Commande validée.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/<order_id>/ship', methods=['POST'])
@admin_required
def ship_order(order_id):
    """Expédier une commande."""
    try:
        current_app.order_service.backoffice_ship_order(session['user_id'], order_id)
        flash('Commande expédiée.', 'success')
    except (PermissionError, ValueError) as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.orders'))