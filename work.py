from flask import Blueprint, jsonify, request
from model import works_schema, work_schema, Task, db, Work
from decorators import token_required
from cerberus import Validator
import datetime
import json


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


@work_api.route('/api/v1/tasks/<task_id>/works', methods=['POST'])
@token_required
def create_work(current_user, task_id):
    """Crea un dia trabajado."""
    try:
        data = json.loads(request.data)
    except:
        return jsonify({'message': 'Bad request'}), 400

    task = Task.query.filter_by(task_id=task_id).first()

    if not task:
        return jsonify({'message': 'No task found!'}), 404

    if current_user not in task.project.members:
        return jsonify({'message': 'You don\'t have permission to edit this task!'}), 403

    to_date = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d')
    schema = {
        'date': {'type': 'date', 'empty': False, 'coerce': to_date, 'required': True},
        'time': {'type': 'float', 'empty': False, 'required': True}
    }

    validator = Validator(schema)

    if validator.validate(data):
        if Work.query.filter_by(date=data['date']).first():
            return jsonify({'message': 'There\'s already work on that date!'}), 400
        else:
            data['user_id'] = current_user.user_id
            data['task_id'] = task.task_id
            work = Work(**data)
            db.session.add(work)
            db.session.commit()
            return jsonify({'message': 'Work created!', 'work': work_schema.dump(work).data}), 201
    else:
        return jsonify({'message': 'Work not created!', 'errors': validator.errors}), 400


@work_api.route('/api/v1/works/<work_id>', methods=['POST'])
@token_required
def modify_work(current_user, work_id):
    """Modifica un dia trabajado."""
    try:
        data = json.loads(request.data)
    except:
        return jsonify({'message': 'Bad request'}), 400

    work = Work.query.filter_by(work_id=work_id).first()

    if not work:
        return jsonify({'message': 'No work found!'}), 404

    if current_user.user_id != work.user_id:
        return jsonify({'message': 'You don\'t have permission to edit this work!'}), 403

    schema = {
        'time': {'type': 'float', 'empty': False, 'required': True}
    }

    validator = Validator(schema)

    if validator.validate(data):
        work.time = data["time"]
        db.session.commit()
        return jsonify({'message': 'Work modified!', 'work': work_schema.dump(work).data})
    else:
        return jsonify({'message': 'Work not created!', 'errors': validator.errors}), 400
