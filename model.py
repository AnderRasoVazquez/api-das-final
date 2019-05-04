from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from cerberus import Validator
import uuid

db = SQLAlchemy()
ma = Marshmallow()


def generate_uuid():
    """Genera un uuid"""
    return str(uuid.uuid4())


class User(db.Model):
    """Tabla usuarios de la base de datos."""
    user_id = db.Column(db.String(50), unique=True, primary_key=True, default=generate_uuid)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(80), nullable=False)

    projects = db.relationship('Project', backref=db.backref('user'))


_user_creation_schema = {
    'email': {'type': 'string', 'required': True, 'empty': False},
    'password': {'type': 'string', 'required': True, 'empty': False}
}
create_user_validator = Validator(_user_creation_schema)


class Project(db.Model):
    """Tabla proyectos de la base de datos."""
    project_id = db.Column(db.String(50), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id', ondelete='CASCADE'))

    requests = db.relationship('Request', backref=db.backref('project'))


_project_creation_schema = {
    'name': {'type': 'string', 'required': True, 'empty': False},
}
create_project_validator = Validator(_project_creation_schema)

_project_update_schema = {
    'name': {'type': 'string', 'empty': False},
}
update_project_validator = Validator(_project_update_schema)


class Request(db.Model):
    """Tabla request de la base de datos"""
    request_id = db.Column(db.String(50), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500))
    body = db.Column(db.Text)
    method = db.Column(db.String(50))

    project_id = db.Column(db.String(50), db.ForeignKey('project.project_id', ondelete='CASCADE'))

    headers = db.relationship('Header', backref=db.backref('request'))


_request_creation_schema = {
    'name': {'type': 'string', 'required': True, 'empty': False},
}
create_request_validator = Validator(_request_creation_schema)

_request_update_schema = {
    'name': {'type': 'string', 'empty': False},
    'url': {'type': 'string', 'empty': False},
    'body': {'type': 'string', 'empty': False},
    'method': {'type': 'string', 'empty': False},
    'headers': {'type': 'list', 'empty': False,
                'schema': {'type': 'dict', 'schema': {
                                                        'key': {'type': 'string', 'empty': False},
                                                        'value': {'type': 'string', 'empty': False},
                                                      }
                           }
                }
}

update_request_validator = Validator(_request_update_schema)


class Header(db.Model):
    """Tabla header de la base de datos"""
    header_id = db.Column(db.String(50), primary_key=True, default=generate_uuid)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)

    request_id = db.Column(db.String(50), db.ForeignKey('request.request_id', ondelete='CASCADE'))


class UserSchema(ma.ModelSchema):
    """Esquema para la clase usuario."""

    class Meta:
        fields = ('user_id', 'email', 'projects')

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("user_api.get_one_user", user_id="<user_id>"),
         "collection": ma.URLFor("user_api.get_all_users")
         }
    )


class ProjectSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""

    class Meta:
        model = Project

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("project_api.get_one_project", project_id="<project_id>"),
         "collection": ma.URLFor("project_api.get_user_projects")}
    )


class RequestSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""

    class Meta:
        model = Request

    headers = ma.Nested('HeaderSchema', many=True, exclude=('header_id', 'request'))
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("request_api.get_one_request", request_id="<request_id>"),
         "collection": ma.URLFor("request_api.get_project_requests", project_id="<project_id>")}
    )


class HeaderSchema(ma.ModelSchema):
    """Esquema para la clase Header."""

    class Meta:
        model = Header


user_schema = UserSchema()
users_schema = UserSchema(many=True)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
request_schema = RequestSchema()
requests_schema = RequestSchema(many=True)
header_schema = HeaderSchema()
headers_schema = HeaderSchema(many=True)
