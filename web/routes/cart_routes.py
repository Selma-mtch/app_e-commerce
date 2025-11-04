"""Routes du panier."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from web.utils.decorators import login_required

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/')
@login_required
def view():
    """Affichage du panier."""
    cart = current_app.cart_service.view_cart(session['user_id'])
    # total = current_app.cart_service.cart_total(session['user_id'])
    
    total = 0

    # Enrichir les items avec les infos produit
    items_with_details = []
    for item in cart.items.values():
        product = current_app.products_repo.get(item.product_id)
        if not product:
            continue

        price_eur = product.price_cents / 100
        subtotal = price_eur * item.quantity
        total += subtotal

        items_with_details.append({
            'product': product,
            'quantity': item.quantity,
            'price': price_eur,
            'total': subtotal
            # 'subtotal': product.price_cents * item.quantity
        })
    
    return render_template('cart/view.html', items=items_with_details, total=total)


@cart_bp.route('/add/<product_id>', methods=['POST'])
@login_required
def add(product_id):
    """Ajouter au panier."""
    try:
        qty_raw = request.form.get('quantity', 1)
        try:
            qty = int(qty_raw)
        except (TypeError, ValueError):
            qty = 1

        current_app.cart_service.add_to_cart(session['user_id'], product_id, qty)
        flash('Produit ajouté au panier !', 'success')
    except ValueError as e:
        # Cas courant: produit introuvable (page obsolète / ID périmé)
        flash(str(e) or 'Produit introuvable ou indisponible. Rafraîchissez la page.', 'warning')
        if request.headers.get('HX-Request'):
            # Retourner le compteur tel quel sans erreur 500
            cart = current_app.cart_service.view_cart(session['user_id'])
            cart_count = sum(item.quantity for item in cart.items.values())
            return f'<span id="cart-count" class="badge bg-primary">{cart_count}</span>'
        return redirect(url_for('catalog.products'))
    except Exception:
        flash("Impossible d'ajouter au panier. Veuillez réessayer.", 'danger')
        if request.headers.get('HX-Request'):
            cart = current_app.cart_service.view_cart(session['user_id'])
            cart_count = sum(item.quantity for item in cart.items.values())
            return f'<span id="cart-count" class="badge bg-primary">{cart_count}</span>'
        return redirect(url_for('catalog.products'))
    # try:
    #     current_app.cart_service.add_to_cart(session['user_id'], product_id, qty)
        
    #     cart = session.get('cart', [])
    #     for _ in range(qty):
    #         cart.append(product_id)
    #     session['cart'] = cart

    #     flash('Produit ajouté au panier !', 'success')
    # except ValueError as e:
    #     flash(str(e), 'danger')

    # Compter les articles depuis le vrai panier
    cart = current_app.cart_service.view_cart(session['user_id'])
    cart_count = sum(item.quantity for item in cart.items.values())
    if request.headers.get('HX-Request'):
        return f'<span id="cart-count" class="badge bg-primary">{cart_count}</span>'
    
    return redirect(url_for('catalog.products'))


@cart_bp.route('/remove/<product_id>', methods=['POST'])
@login_required
def remove(product_id):
    """Retirer du panier."""
    current_app.cart_service.remove_from_cart(session['user_id'], product_id, qty=0)
    flash('Produit retiré du panier.', 'info')
    return redirect(url_for('cart.view'))
