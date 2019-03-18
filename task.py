from flask import Blueprint, jsonify
from model import Task
from model import tasks_schema


task_api = Blueprint('task_api', __name__)


@task_api.route('/api/v1/tasks', methods=['GET'])
# @token_required
# @admin_required
# def get_all_tasks(current_user):
def get_all_tasks():
    """Devolver todas las tareas."""
    tasks = Task.query.all()
    output = tasks_schema.dump(tasks)
    return jsonify({"tasks": output.data})
