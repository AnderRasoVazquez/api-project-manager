from flask import Blueprint, jsonify
from model import tasks_schema, Project, Task, task_schema, db
from decorators import token_required


task_api = Blueprint('task_api', __name__)


@task_api.route('/api/v1/projects/<project_id>/tasks', methods=['GET'])
@token_required
def get_all_tasks(current_user, project_id):
    """Devolver todas las tareas."""
    # TODO delete project tiene el mismo codigo, igual deberia hacer un decorator
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user not in project.members:
        return jsonify({'message': 'You don\'t have permission to access these tasks!'}), 403

    tasks = project.tasks

    output = tasks_schema.dump(tasks)
    return jsonify({"tasks": output.data})


@task_api.route('/api/v1/tasks/<task_id>', methods=['GET'])
@token_required
def get_one_task(current_user, task_id):
    """Devolver una tarea."""
    task = Task.query.filter_by(task_id=task_id).first()

    if not task:
        return jsonify({'message': 'No task found!'}), 404

    if current_user not in task.project.members:
        return jsonify({'message': 'You don\'t have permission to access this task!'}), 403

    return jsonify({"task": task_schema.dump(task).data})


@task_api.route('/api/v1/tasks/<task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    """Eliminar una tarea."""
    task = Task.query.filter_by(task_id=task_id).first()

    if not task:
        return jsonify({'message': 'No task found!'}), 404

    if current_user not in task.project.members:
        return jsonify({'message': 'You don\'t have permission to access this task!'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'The task has been deleted!'})

# TODO create task
# TODO edit task
