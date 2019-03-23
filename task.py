from flask import Blueprint, jsonify
from model import tasks_schema, Project, Task, task_schema, db, create_task_validator, update_task_validator
from decorators import token_required, load_data


task_api = Blueprint('task_api', __name__)


@task_api.route('/api/v1/projects/<project_id>/tasks', methods=['GET'])
@token_required
def get_all_tasks(current_user, project_id):
    """Devolver todas las tareas."""
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


@task_api.route('/api/v1/projects/<project_id>/tasks', methods=['POST'])
@token_required
@load_data
def create_task(data, current_user, project_id):
    """Crea una tarea."""
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user not in project.members:
        return jsonify({'message': 'You don\'t have permission to delete that project!'}), 403

    if create_task_validator.validate(data):
        task = Task(**data)
        db.session.add(task)
        project.tasks.append(task)
        db.session.commit()
        return jsonify({'message': 'New task created!', 'task': task_schema.dump(task).data}), 201
    else:
        return jsonify({'message': 'Task not created!', 'errors': create_task_validator.errors}), 400


@task_api.route('/api/v1/tasks/<task_id>', methods=['POST'])
@token_required
@load_data
def modify_task(data, current_user, task_id):
    """Modifica una tarea."""
    task = Task.query.filter_by(task_id=task_id).first()

    if not task:
        return jsonify({'message': 'No task found!'}), 404

    if current_user not in task.project.members:
        return jsonify({'message': 'You don\'t have permission to edit this task!'}), 403

    if update_task_validator.validate(data):
        for key, value in data.items():
            setattr(task, key, value)
        db.session.commit()
        return jsonify({'message': 'Task modified!', 'task': task_schema.dump(task).data})
    else:
        return jsonify({'message': 'Task not modified!', 'errors': update_task_validator.errors}), 400
