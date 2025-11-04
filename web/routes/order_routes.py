"""Routes des commandes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from web.utils.decorators import login_required

order_bp = Blueprint('orders', __name__, url_prefix='/orders')


@order_bp.route('/')
@login_required
def list_orders():
    """Liste des commandes de l'utilisateur."""
    orders = current_app.order_service.view_orders(session['user_id'])
    return render_template('orders/list.html', orders=orders)


@order_bp.route('/<order_id>')
@login_required
def detail(order_id):
    """Détail d'une commande."""
    order = current_app.orders_repo.get(order_id)
    if not order or order.user_id != session['user_id']:
        flash('Commande introuvable.', 'danger')
        return redirect(url_for('orders.list_orders'))
    
    return render_template('orders/detail.html', order=order)


@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Page de checkout et paiement."""
    if request.method == 'POST':
        try:
            # Créer la commande
            order = current_app.order_service.checkout(session['user_id'])
            
            # Payer
            payment = current_app.order_service.pay_by_card(
                order.id,
                request.form['card_number'],
                int(request.form['exp_month']),
                int(request.form['exp_year']),
                request.form['cvc']
            )
            
            flash(f'Commande passée avec succès ! Numéro: {order.id[:8]}...', 'success')
            return redirect(url_for('orders.detail', order_id=order.id))
        except ValueError as e:
            flash(str(e), 'danger')
    
    cart = current_app.cart_service.view_cart(session['user_id'])
    total_cents = current_app.cart_service.cart_total(session['user_id'])
    total = (total_cents or 0) / 100
    
    if not cart.items:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('catalog.products'))
    
    return render_template('orders/checkout.html', total=total)


@order_bp.route('/<order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    """Annuler une commande par l'utilisateur."""
    try:
        order = current_app.order_service.request_cancellation(session['user_id'], order_id)
        flash('Commande annulée.', 'info')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('orders.detail', order_id=order_id))
