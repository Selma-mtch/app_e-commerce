"""Routes des commandes."""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user
import requests
from web.utils.decorators import login_required
from web.utils.address import parse_address_fields

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
    def verify_address(address: str, city: str, postcode: str) -> tuple[bool, str | None]:
        """Vérifie l'adresse via l'API adresse.data.gouv.fr."""
        try:
            params = {"q": address, "limit": 1}
            if postcode:
                params["postcode"] = postcode
            resp = requests.get("https://api-adresse.data.gouv.fr/search/", params=params, timeout=4)
            resp.raise_for_status()
            data = resp.json() or {}
            features = data.get("features") or []
            if not features:
                return False, None
            props = features[0].get("properties", {})
            score = props.get("score", 0)
            found_city = (props.get("city") or props.get("name") or "").strip()
            found_postcode = (props.get("postcode") or "").strip()

            if score < 0.5:
                return False, found_city

            def norm(val: str) -> str:
                return val.strip().casefold()

            if city and found_city and norm(city) != norm(found_city):
                return False, found_city
            if postcode and found_postcode and postcode != found_postcode:
                return False, found_city
            return True, found_city
        except Exception:
            return False, None

    cart = current_app.cart_service.view_cart(session['user_id'])
    total_cents = current_app.cart_service.cart_total(session['user_id'])
    total = (total_cents or 0) / 100
    addr_fields = parse_address_fields(getattr(current_user, "address", None))
    full_name_prefill = " ".join(
        part for part in [getattr(current_user, "first_name", ""), getattr(current_user, "last_name", "")]
        if part
    ).strip()
    items_with_details = []
    for item in cart.items.values():
        product = current_app.products_repo.get(item.product_id)
        if not product:
            continue
        price_eur = product.price_cents / 100
        items_with_details.append({
            'product': product,
            'quantity': item.quantity,
            'price': price_eur,
            'subtotal': price_eur * item.quantity,
        })

    if not cart.items:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('catalog.products'))

    if request.method == 'POST':
        errors = []
        now = datetime.now()

        # Adresse et cohérence ville/CP
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        postcode = request.form.get('zip', '').strip()
        country = request.form.get('country', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()

        if not address:
            errors.append("L'adresse est obligatoire.")
        if len(address) > 200:
            errors.append("Adresse trop longue (200 caractères max).")
        if country and country.lower() not in {"france", "fr", "français", "republique francaise"}:
            errors.append("Seules les adresses en France métropolitaine sont prises en charge pour l'instant.")
        if city and len(city) > 100:
            errors.append("Ville trop longue (100 caractères max).")
        if postcode and len(postcode) > 20:
            errors.append("Code postal trop long (20 caractères max).")
        if country and len(country) > 60:
            errors.append("Pays trop long (60 caractères max).")
        if full_name and len(full_name) > 120:
            errors.append("Nom complet trop long (120 caractères max).")
        if phone and len(phone) > 30:
            errors.append("Téléphone trop long (30 caractères max).")

        is_valid_addr, found_city = verify_address(address, city, postcode)
        if not is_valid_addr:
            errors.append("Adresse introuvable ou incohérente, vérifiez l'adresse et la ville.")
        elif city and found_city and city.strip().casefold() != found_city.strip().casefold():
            errors.append(f"Ville incohérente avec l'adresse (détectée : {found_city}).")

        card_number_raw = request.form.get('card_number', '')
        card_number = ''.join(ch for ch in card_number_raw if ch.isdigit())
        if not (card_number.isdigit() and 13 <= len(card_number) <= 19):
            errors.append("Numéro de carte invalide (13 à 19 chiffres).")
        else:
            def luhn_valid(num: str) -> bool:
                total = 0
                reverse_digits = num[::-1]
                for idx, ch in enumerate(reverse_digits):
                    d = int(ch)
                    if idx % 2 == 1:
                        d *= 2
                        if d > 9:
                            d -= 9
                    total += d
                return total % 10 == 0

            if not luhn_valid(card_number):
                errors.append("Numéro de carte invalide (contrôle Luhn).")

        exp_month_raw = request.form.get('exp_month', '').strip()
        exp_year_raw = request.form.get('exp_year', '').strip()
        exp_month = None
        try:
            exp_month_candidate = int(exp_month_raw)
            if 1 <= exp_month_candidate <= 12:
                exp_month = exp_month_candidate
            else:
                errors.append("Mois d'expiration invalide.")
        except (TypeError, ValueError):
            errors.append("Mois d'expiration invalide.")

        exp_year = None
        try:
            exp_year_candidate = int(exp_year_raw)
            if exp_year_candidate > now.year + 20:
                errors.append("Année d'expiration invalide.")
            elif exp_year_candidate < now.year:
                # Annee passée => expirée
                errors.append("La carte est expirée.")
            else:
                exp_year = exp_year_candidate
        except (TypeError, ValueError):
            errors.append("Année d'expiration invalide.")

        if exp_year and exp_month and (exp_year, exp_month) < (now.year, now.month):
            errors.append("La carte est expirée.")

        cvc = request.form.get('cvc', '').strip()
        if not (cvc.isdigit() and 3 <= len(cvc) <= 4):
            errors.append("CVC invalide (3 ou 4 chiffres).")

        if errors:
            for msg in errors:
                flash(msg, 'warning')
        else:
            try:
                # Créer la commande
                order = current_app.order_service.checkout(session['user_id'])

                # Payer
                current_app.order_service.pay_by_card(
                    order.id,
                    card_number,
                    exp_month,
                    exp_year,
                    cvc
                )

                flash(f'Commande passée avec succès ! Numéro: {order.id[:8]}...', 'success')
                return redirect(url_for('orders.detail', order_id=order.id))
            except ValueError as e:
                flash(str(e), 'danger')

    return render_template(
        'orders/checkout.html',
        total=total,
        items=items_with_details,
        current_year=datetime.now().year,
        current_month=datetime.now().month,
        addr_fields=addr_fields,
        full_name_prefill=full_name_prefill
    )


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
