from flask import  Blueprint, jsonify

from model import Request, Header, db, User, create_request_validator, update_request_validator, request_schema, requests_schema, Project
from decorators import token_required, load_data


request_api = Blueprint('request_api', __name__)


@request_api.route('/api/v1/projects/<project_id>/requests', methods=['GET'])
@token_required
def get_project_requests(current_user, project_id):
    """Devolver todas las requests."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user != project.user:
        return jsonify({'message': 'You don\'t have permission to access these requests!'}), 403

    the_requests = project.requests

    output = requests_schema.dump(the_requests)
    data = output.data
    data.sort(key=lambda x: x["name"].lower())
    return jsonify({"requests": data})


@request_api.route('/api/v1/requests/<request_id>', methods=['GET'])
@token_required
def get_one_request(current_user, request_id):
    """Devuelve una request."""
    one_request = Request.query.filter_by(request_id=request_id).first()

    if not one_request:
        return jsonify({'message': 'No request found!'}), 404

    if current_user != one_request.project.user:
        return jsonify({'message': 'You don\'t have permission to access that request!'}), 403

    return jsonify({'request': request_schema.dump(one_request).data})


@request_api.route('/api/v1/projects/<project_id>/requests', methods=['POST'])
@token_required
@load_data
def create_request(data, current_user: User, project_id):
    """Crea una request."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user != project.user:
        return jsonify({'message': 'You don\'t have permission to create a request in that project!'}), 403

    if create_request_validator.validate(data):
        for req in project.requests:
            if req.name == data['name']:
                return jsonify({'message': 'A request with that name already exists'}), 409
        one_request = Request(**data)
        db.session.add(one_request)
        project.requests.append(one_request)
        db.session.commit()
        return jsonify({'message': 'New request created!', 'request': request_schema.dump(one_request).data})
    else:
        return jsonify({'message': 'Request not created!', 'errors': create_request_validator.errors}), 400


@request_api.route('/api/v1/requests/<request_id>', methods=['DELETE'])
@token_required
def delete_request(current_user, request_id):
    """Devuelve una request."""
    one_request = Request.query.filter_by(request_id=request_id).first()

    if not one_request:
        return jsonify({'message': 'No request found!'}), 404

    if current_user != one_request.project.user:
        return jsonify({'message': 'You don\'t have permission to delete that request!'}), 403

    db.session.delete(one_request)
    db.session.commit()
    return jsonify({'message': 'The request has been deleted!'})


@request_api.route('/api/v1/requests/<request_id>', methods=['POST'])
@token_required
@load_data
def update_request(data, current_user, request_id):
    """Actualiza una request."""
    one_request = Request.query.filter_by(request_id=request_id).first()

    if not one_request:
        return jsonify({'message': 'No request found!'}), 404

    if current_user != one_request.project.user:
        return jsonify({'message': 'You don\'t have permission to update that request!'}), 403

    if update_request_validator.validate(data):
        # no actualizar si ya existe una request con ese nombre
        if Request.query.filter(Request.name == data['name'], Request.request_id != one_request.request_id).first():
            return jsonify({'message': 'A request with that name already exists'}), 409

        # eliminar las header anteriores
        for previous_header in one_request.headers:
            db.session.delete(previous_header)

        # rellenar datos de la header
        for key, value in data.items():
            # añadir directamente los campos que no sean las headers
            if key != "headers":
                setattr(one_request, key, value)
            # gestionar las headers
            else:
                # crear las nuevas headers
                for new_header_data in value:
                    header = Header(**new_header_data)
                    one_request.headers.append(header)
        db.session.commit()
        return jsonify({'message': 'Request updated!', 'request': request_schema.dump(one_request).data})
    else:
        return jsonify({'message': 'Request not updated!', 'errors': update_request_validator.errors}), 400
