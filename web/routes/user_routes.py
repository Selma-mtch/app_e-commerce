from flask import Blueprint, render_template
from flask_login import login_required, current_user

from web.utils.address import parse_address_fields

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/account')
@login_required
def account():
    address_fields = parse_address_fields(current_user.address)
    return render_template('user/account.html', user=current_user, address_fields=address_fields)
