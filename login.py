from flask import Blueprint, jsonify, request, make_response
from flask import current_app as app
from model import User
from werkzeug.security import check_password_hash
import datetime
import jwt

login_api = Blueprint('login_api', __name__)


def login_error():
    """Devuelve una respuesta indicando el error al intentar hacer login."""
    return make_response(jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@login_api.route('/api/v1/login')
def login():
    """Inicio de sesion. Devuelve un token para usarlo despues."""
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return login_error()

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return login_error()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'user_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*360)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    # pass no es correcto
    return login_error()
