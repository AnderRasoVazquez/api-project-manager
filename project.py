from flask import Blueprint, jsonify
from model import Project
from model import projects_schema


project_api = Blueprint('project_api', __name__)


@project_api.route('/api/v1/projects', methods=['GET'])
# @token_required
# @admin_required
# def get_all_tasks(current_user):
def get_all_projects():
    """Devolver todos los proyectos."""
    projects = Project.query.all()
    output = projects_schema.dump(projects)
    return jsonify({"projects": output.data})
