from functools import wraps
from flask import request, jsonify
from flask import current_app as app
import jwt
import json

from model import User


def token_required(f):
    """Decorator para comprobar que el token es valido antes de ejecutar la funcion."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message': 'Wrong token!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def load_data(f):
    """Decorator para comprobar que el json enviado esta bien formateado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            data = json.loads(request.data)
        except:
            return jsonify({'message': 'JSON bad formatted!'}), 400
        return f(data, *args, **kwargs)
    return decorated
