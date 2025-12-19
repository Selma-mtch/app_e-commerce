"""Routes backoffice admin."""

import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from models.product import Product
from web.utils.decorators import admin_required

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _save_uploaded_image(image_file):
    """Save uploaded image under static/uploads and return the relative path."""
    if not image_file or not getattr(image_file, 'filename', ''):
        return None

    filename = secure_filename(image_file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if not ext or ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError('Format de fichier non supporté (png, jpg, jpeg, webp, gif).')

    year = datetime.utcnow().strftime('%Y')
    month = datetime.utcnow().strftime('%m')
    fname = f"{uuid.uuid4()}.{ext}"
    rel_dir = os.path.join(current_app.config.get('UPLOADS_SUBDIR', 'uploads'), year, month)
    save_dir = os.path.join(current_app.static_folder, rel_dir)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, fname)
    image_file.save(save_path)
    return os.path.join(current_app.config.get('UPLOADS_SUBDIR', 'uploads'), year, month, fname).replace('\\', '/')


def _delete_local_image(rel_path):
    """Remove a previously uploaded image from disk if it lives under uploads/."""
    if not rel_path or rel_path.startswith(('http://', 'https://')):
        return
    uploads_root = os.path.normpath(
        os.path.join(current_app.static_folder, current_app.config.get('UPLOADS_SUBDIR', 'uploads'))
    )
    candidate = rel_path.lstrip('/\\')
    candidate_path = os.path.normpath(os.path.join(current_app.static_folder, candidate))
    try:
        if os.path.commonpath([candidate_path, uploads_root]) != uploads_root:
            return
    except ValueError:
        return
    if os.path.isfile(candidate_path):
        try:
            os.remove(candidate_path)
        except OSError:
            pass


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Tableau de bord admin avec indicateurs clés."""
    users_count = (
        len(current_app.users_repo.list_all())
        if hasattr(current_app.users_repo, 'list_all')
        else len(getattr(current_app.users_repo, '_by_id', {}))
    )
    products_count = (
        len(current_app.products_repo.list_all())
        if hasattr(current_app.products_repo, 'list_all')
        else len(getattr(current_app.products_repo, '_by_id', {}))
    )
    orders_count = (
        len(current_app.orders_repo.list_all())
        if hasattr(current_app.orders_repo, 'list_all')
        else len(getattr(current_app.orders_repo, '_by_id', {}))
    )
    invoices_count = (
        len(current_app.invoices_repo.list_all())
        if hasattr(current_app.invoices_repo, 'list_all')
        else len(getattr(current_app.invoices_repo, '_by_id', {}))
    )
    payments_count = (
        len(current_app.payments_repo.list_all())
        if hasattr(current_app.payments_repo, 'list_all')
        else len(getattr(current_app.payments_repo, '_by_id', {}))
    )
    threads_count = (
        len(current_app.threads_repo.list_all())
        if hasattr(current_app.threads_repo, 'list_all')
        else len(getattr(current_app.threads_repo, '_by_id', {}))
    )
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
    if hasattr(current_app.orders_repo, 'list_all'):
        all_orders = current_app.orders_repo.list_all()
    else:
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
    if hasattr(current_app.products_repo, 'list_all'):
        products = current_app.products_repo.list_all()
    else:
        products = list(getattr(current_app.products_repo, '_by_id', {}).values())
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    """Formulaire de création d'un produit."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_eur = request.form.get('price_eur', '').strip()
        stock_qty = request.form.get('stock_qty', '').strip()
        active = True if request.form.get('active') == 'on' else False

        if not name or not description or not price_eur or not stock_qty:
            flash('Tous les champs obligatoires doivent être remplis.', 'danger')
            return render_template('admin/product_form.html', mode='new', product=None)
        try:
            price_cents = int(round(float(price_eur.replace(',', '.')) * 100))
            qty = int(stock_qty)
            if price_cents < 0 or qty < 0:
                raise ValueError
        except Exception:
            flash("Prix ou stock invalide.", 'danger')
            return render_template('admin/product_form.html', mode='new', product=None)

        p = Product(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            price_cents=price_cents,
            stock_qty=qty,
            active=active,
        )

        image_field_url = request.form.get('image_url', '').strip()
        image_file = request.files.get('image_file')
        try:
            if image_field_url:
                p.image_url = image_field_url
            elif image_file and getattr(image_file, 'filename', ''):
                uploaded = _save_uploaded_image(image_file)
                if uploaded:
                    p.image_url = uploaded
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('admin/product_form.html', mode='new', product=p)

        try:
            current_app.products_repo.add(p)
            flash('Produit créé avec succès.', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            flash(f"Erreur lors de la création: {e}", 'danger')
            return render_template('admin/product_form.html', mode='new', product=None)

    return render_template('admin/product_form.html', mode='new', product=None)


@admin_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Edition d'un produit (y compris l'image)."""
    product = current_app.products_repo.get(product_id)
    if not product:
        flash('Produit introuvable.', 'danger')
        return redirect(url_for('admin.products'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_eur = request.form.get('price_eur', '').strip()
        stock_qty = request.form.get('stock_qty', '').strip()
        active = True if request.form.get('active') == 'on' else False
        remove_image = True if request.form.get('remove_image') == 'on' else False

        if not name or not description or not price_eur or not stock_qty:
            flash('Tous les champs obligatoires doivent être remplis.', 'danger')
            return render_template('admin/product_form.html', mode='edit', product=product)
        try:
            price_cents = int(round(float(price_eur.replace(',', '.')) * 100))
            qty = int(stock_qty)
            if price_cents < 0 or qty < 0:
                raise ValueError
        except Exception:
            flash("Prix ou stock invalide.", 'danger')
            return render_template('admin/product_form.html', mode='edit', product=product)

        image_field_url = request.form.get('image_url', '').strip()
        image_file = request.files.get('image_file')
        previous_image = product.image_url
        new_image_url = previous_image

        try:
            if image_field_url:
                new_image_url = image_field_url
            elif image_file and getattr(image_file, 'filename', ''):
                uploaded = _save_uploaded_image(image_file)
                if uploaded:
                    new_image_url = uploaded
            elif remove_image:
                new_image_url = None
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('admin/product_form.html', mode='edit', product=product)

        product.name = name
        product.description = description
        product.price_cents = price_cents
        product.stock_qty = qty
        product.active = active
        product.image_url = new_image_url

        try:
            current_app.products_repo.add(product)
            if (remove_image or new_image_url != previous_image) and previous_image:
                _delete_local_image(previous_image)
            flash('Produit mis à jour.', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour: {e}", 'danger')
            return render_template('admin/product_form.html', mode='edit', product=product)

    return render_template('admin/product_form.html', mode='edit', product=product)


@admin_bp.route('/products/<product_id>/toggle', methods=['POST'])
@admin_required
def toggle_product(product_id):
    """Active/désactive un produit."""
    p = current_app.products_repo.get(product_id)
    if not p:
        flash('Produit introuvable.', 'danger')
        return redirect(url_for('admin.products'))
    p.active = not p.active
    try:
        current_app.products_repo.add(p)
    except Exception:
        pass
    if not p.active:
        affected = current_app.carts_repo.remove_product_everywhere(product_id)
        flash((f'Produit désactivé et retiré de {affected} panier(s).' if affected else 'Produit désactivé.'), 'info')
    else:
        flash('Produit activé.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/support')
@admin_required
def support():
    """Liste des tickets support (admin)."""
    if hasattr(current_app.threads_repo, 'list_all'):
        threads = current_app.threads_repo.list_all()
    else:
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
            current_app.customer_service.post_message(thread_id=thread.id, author_user_id=None, body=body)
            flash('Réponse envoyée.', 'success')
            return redirect(url_for('admin.support_thread', thread_id=thread.id))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('admin/support_thread.html', thread=thread)
