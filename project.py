from flask import Blueprint, jsonify, request
from model import Project, projects_schema, db, User, project_schema
from decorators import token_required, admin_required
from cerberus import Validator
import json

project_api = Blueprint('project_api', __name__)


@project_api.route('/api/v1/projects/all', methods=['GET'])
@token_required
@admin_required
def get_all_projects(current_user):
    """Devolver todos los proyectos."""
    projects = Project.query.all()
    output = projects_schema.dump(projects)
    return jsonify({"projects": output.data})


# TODO diferencia?
@project_api.route('/api/v1/projects', methods=['GET'])
@token_required
def get_user_projects(current_user):
    """Devolver todos los proyectos."""
    projects = current_user.projects
    output = projects_schema.dump(projects)
    return jsonify({"projects": output.data})


@project_api.route('/api/v1/projects', methods=['POST'])
@token_required
def create_project(current_user: User):
    """Devolver todos los proyectos."""
    try:
        data = json.loads(request.data)
    except:
        return jsonify({'message': 'Bad request'}), 400

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False},
        'desc': {'type': 'string', 'empty': False}
    }
    validator = Validator(schema)

    if validator.validate(data):
        project = Project(**data)
        db.session.add(project)
        current_user.projects.append(project)
        db.session.commit()
        return jsonify({'message': 'New project created!', 'project': project_schema.dump(project).data}), 201
    else:
        return jsonify({'message': 'Project not created!', 'errors': validator.errors}), 400


@project_api.route('/api/v1/projects/<project_id>', methods=['DELETE'])
@token_required
def delete_project(current_user, project_id):
    """Elimina un proyecto."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user not in project.members:
        return jsonify({'message': 'You don\'t have permission to delete that project!'}), 403

    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'The project has been deleted!'})


@project_api.route('/api/v1/projects/<project_id>', methods=['GET'])
@token_required
def get_one_project(current_user, project_id):
    """Devuelve un proyecto."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user not in project.members:
        return jsonify({'message': 'You don\'t have permission to delete that project!'}), 403

    return jsonify({'project': project_schema.dump(project).data})


# TODO edit project
