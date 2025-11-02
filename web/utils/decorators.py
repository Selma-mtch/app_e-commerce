"""Décorateurs utilitaires pour les routes."""

from functools import wraps
from flask import session, redirect, url_for, flash, current_app


def login_required(f):
    """Décorateur pour protéger les routes nécessitant une connexion."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Décorateur pour protéger les routes nécessitant des droits admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté.', 'danger')
            return redirect(url_for('auth.login'))
        
        user = current_app.users_repo.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Accès interdit : droits administrateur requis.', 'danger')
            return redirect(url_for('catalog.products'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Récupère l'utilisateur actuellement connecté."""
    if 'user_id' in session:
        return current_app.users_repo.get(session['user_id'])
    return None