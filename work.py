from flask import Blueprint, jsonify
from model import works_schema, work_schema, Task, db, Work
from decorators import token_required


work_api = Blueprint('work_api', __name__)


@work_api.route('/api/v1/tasks/<task_id>/works', methods=['GET'])
@token_required
def get_all_task_work(current_user, task_id):
    """Devolver todos los dias trabajados en una tarea."""
    task = Task.query.filter_by(task_id=task_id).first()

    if not task:
        return jsonify({'message': 'No task found!'}), 404

    if current_user not in task.project.members:
        return jsonify({'message': 'You don\'t have permission to access task\'s work!'}), 403

    works = task.works

    output = works_schema.dump(works)
    return jsonify({"works": output.data})


@work_api.route('/api/v1/works/<work_id>', methods=['GET'])
@token_required
def get_one_work(current_user, work_id):
    """Devolver un dia trabajado."""
    work = Work.query.filter_by(work_id=work_id).first()

    if not work:
        return jsonify({'message': 'No work found!'}), 404

    if current_user not in work.task.project.members:
        return jsonify({'message': 'You don\'t have permission to access this work!'}), 403

    return jsonify({"work": work_schema.dump(work).data})


@work_api.route('/api/v1/works/<work_id>', methods=['DELETE'])
@token_required
def delete_work(current_user, work_id):
    """Eliminar un dia trabajado."""
    work = Work.query.filter_by(work_id=work_id).first()

    if not work:
        return jsonify({'message': 'No work found!'}), 404

    if current_user not in work.task.project.members:
        return jsonify({'message': 'You don\'t have permission to delete this work!'}), 403

    db.session.delete(work)
    db.session.commit()
    return jsonify({'message': 'The work has been deleted!'})


# TODO create work
# TODO delete work
