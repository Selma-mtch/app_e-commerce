from flask import Blueprint, render_template
from flask_login import login_required, current_user

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/account')
@login_required
def account():
    return render_template('user/account.html', user=current_user)
