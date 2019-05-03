from flask import Flask, jsonify
from werkzeug.security import generate_password_hash
from model import *
from login import login_api
from project import project_api
from user import user_api
from flask_heroku import Heroku

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

if 'HEROKU' in os.environ:  # heroku config:set HEROKU=1
    heroku = Heroku(app)
else:  # local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///das'  # postgresql


db.init_app(app)
ma.init_app(app)


def initial_setup():
    """Ejecutar desde la terminal para crear la base de datos y datos de prueba.
    heroku run python3
    import api
    api.initial_setup()
    """
    with app.app_context():
        db.create_all()
        _add_initial_values()


def _add_initial_values():
    """Añadir valores iniciales a la base de datos."""
    hashed_password = generate_password_hash('admin', method='sha256')
    admin = User(email='admin@admin.com', password=hashed_password)
    db.session.add(admin)
    db.session.commit()

    hashed_password = generate_password_hash('user', method='sha256')
    user = User(email='user@user.com', password=hashed_password)
    db.session.add(user)
    db.session.commit()

    project = Project(name='Pokemon API')
    db.session.add(project)
    projectTwo = Project(name='Otra API')
    db.session.add(project)
    db.session.commit()

    admin.projects.append(projectTwo)
    admin.projects.append(project)
    db.session.commit()


app.register_blueprint(login_api)
app.register_blueprint(user_api)
# app.register_blueprint(project_api)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

