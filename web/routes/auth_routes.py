"""Routes d'authentification."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription."""
    if request.method == 'POST':
        try:
            user = current_app.auth_service.register(
                email=request.form['email'],
                password=request.form['password'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                address=request.form['address']
            )
            flash(f'Compte créé avec succès ! Bienvenue {user.first_name} !', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    if request.method == 'POST':
        try:
            token = current_app.auth_service.login(
                email=request.form['email'],
                password=request.form['password']
            )
            user_id = current_app.sessions.get_user_id(token)
            session['user_id'] = user_id
            session['token'] = token

            user = current_app.users_repo.get(user_id)
            login_user(user)

            flash(f'Bienvenue {user.first_name} !', 'success')
            return redirect(url_for('catalog.products'))
        except ValueError as e:
            flash('Identifiants invalides.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Déconnexion."""
    if 'token' in session:
        current_app.auth_service.logout(session['token'])
    session.clear()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def profile():
    """Affiche et permet la mise à jour des informations de l'utilisateur."""
    user = current_app.users_repo.get(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'update_profile':
                # Mettre à jour uniquement les champs autorisés
                user.update_profile(
                    first_name=request.form.get('first_name', user.first_name),
                    last_name=request.form.get('last_name', user.last_name),
                    address=request.form.get('address', user.address)
                )
                # Persister les changements (utile notamment en mode DB)
                current_app.users_repo.add(user)
                flash("Profil mis à jour avec succès.", "success")
            elif action == 'change_email':
                current_password = request.form.get('current_password', '')
                new_email = request.form.get('new_email', '')
                current_app.auth_service.change_email(user.id, current_password, new_email)
                flash("Adresse email mise à jour.", "success")
            elif action == 'change_password':
                current_password = request.form.get('current_password', '')
                new_password = request.form.get('new_password', '')
                confirm = request.form.get('confirm_password', '')
                if new_password != confirm:
                    raise ValueError("La confirmation ne correspond pas au nouveau mot de passe.")
                current_app.auth_service.change_password(user.id, current_password, new_password)
                flash("Mot de passe mis à jour.", "success")
            else:
                flash("Action non reconnue.", "warning")
            return redirect(url_for('auth.profile'))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")

    return render_template('user/account.html', current_user=user)
