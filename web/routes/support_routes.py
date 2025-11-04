"""Routes du service client."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from web.utils.decorators import login_required

support_bp = Blueprint('support', __name__, url_prefix='/support')


@support_bp.route('/threads')
@login_required
def threads():
    """Liste des tickets support."""
    user_threads = current_app.customer_service.list_user_threads(session['user_id'])
    return render_template('support/threads.html', threads=user_threads)


@support_bp.route('/threads/new', methods=['GET', 'POST'])
@login_required
def new_thread():
    """Créer un nouveau ticket."""
    if request.method == 'POST':
        thread = current_app.customer_service.open_thread(
            user_id=session['user_id'],
            subject=request.form['subject'],
            order_id=request.form.get('order_id') or None
        )
        
        # Premier message
        current_app.customer_service.post_message(
            thread_id=thread.id,
            author_user_id=session['user_id'],
            body=request.form['message']
        )
        
        flash('Ticket créé avec succès !', 'success')
        return redirect(url_for('support.thread_detail', thread_id=thread.id))
    
    orders = current_app.order_service.view_orders(session['user_id'])
    return render_template('support/new_thread.html', orders=orders)


@support_bp.route('/threads/<thread_id>', methods=['GET', 'POST'])
@login_required
def thread_detail(thread_id):
    """Détail d'un ticket et réponse."""
    thread = current_app.customer_service.get_thread(thread_id)
    if not thread or thread.user_id != session['user_id']:
        flash('Ticket introuvable.', 'danger')
        return redirect(url_for('support.threads'))

    if request.method == 'POST':
        try:
            body = request.form['message']
            current_app.customer_service.post_message(thread_id=thread.id, author_user_id=session['user_id'], body=body)
            flash('Message envoyé.', 'success')
            return redirect(url_for('support.thread_detail', thread_id=thread.id))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('support/thread_detail.html', thread=thread)

