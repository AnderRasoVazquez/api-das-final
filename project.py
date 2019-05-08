from flask import Blueprint, jsonify
from model import Project, projects_schema, db, User, project_schema, create_project_validator, update_project_validator
from decorators import token_required, load_data


project_api = Blueprint('project_api', __name__)


@project_api.route('/api/v1/projects', methods=['GET'])
@token_required
def get_user_projects(current_user):
    """Devolver todos los proyectos."""
    projects = current_user.projects
    output = projects_schema.dump(projects)
    return jsonify({"projects": output.data})


@project_api.route('/api/v1/projects', methods=['POST'])
@token_required
@load_data
def create_project(data, current_user: User):
    """Crea un proyecto."""
    if create_project_validator.validate(data):
        if Project.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'A project with that name already exists'}), 409
        project = Project(**data)
        db.session.add(project)
        current_user.projects.append(project)
        db.session.commit()
        return jsonify({'message': 'New project created!', 'project': project_schema.dump(project).data})
    else:
        return jsonify({'message': 'Project not created!', 'errors': create_project_validator.errors}), 400


@project_api.route('/api/v1/projects/<project_id>', methods=['DELETE'])
@token_required
def delete_project(current_user, project_id):
    """Elimina un proyecto."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user != project.user:
        return jsonify({'message': 'You don\'t have permission to delete that project!'}), 403

    current_user.projects.remove(project)
    db.session.commit()
    return jsonify({'message': 'The project has been deleted!'})


@project_api.route('/api/v1/projects/<project_id>', methods=['GET'])
@token_required
def get_one_project(current_user, project_id):
    """Devuelve un proyecto."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user != project.user:
        return jsonify({'message': 'You don\'t have permission to access that project!'}), 403

    return jsonify({'project': project_schema.dump(project).data})


@project_api.route('/api/v1/projects/<project_id>', methods=['POST'])
@token_required
@load_data
def update_project(data, current_user, project_id):
    """Actualiza un proyecto."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user != project.user:
        return jsonify({'message': 'You don\'t have permission to delete that project!'}), 403

    if update_project_validator.validate(data):
        if Project.query.filter(Project.name == data['name'], Project.project_id != project.project_id).first():
        # if Project.query.filter(Project.name == data['name'] and Project.project_id != project.project_id).first():
        # if Project.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'A project with that name already exists'}), 409
        for key, value in data.items():
            setattr(project, key, value)
        db.session.commit()
        return jsonify({'message': 'Project updated!', 'project': project_schema.dump(project).data})
    else:
        return jsonify({'message': 'Project not updated!', 'errors': update_project_validator.errors}), 400
