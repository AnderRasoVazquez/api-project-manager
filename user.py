from flask import jsonify, request, Blueprint
from cerberus import Validator
from decorators import token_required, admin_required
from werkzeug.security import generate_password_hash
from model import db, User, user_schema, users_schema
import uuid
import json

user_api = Blueprint('user_api', __name__)


@user_api.route('/api/v1/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Devolver todos los usuarios."""
    users = User.query.all()
    output = users_schema.dump(users)
    return jsonify({"users": output.data})


@user_api.route('/api/v1/users', methods=['POST'])
@token_required
def create_user(current_user):
    """Crea un usuario."""
    # TODO esto tendria que ser en todas partes?
    try:
        data = json.loads(request.data)
    except:
        return jsonify({'message': 'Bad request'}), 400

    schema = {
        'email': {'type': 'string', 'required': True, 'empty': False},
        'name': {'type': 'string', 'required': True, 'empty': False},
        'password': {'type': 'string', 'required': True, 'empty': False}
    }
    validator = Validator(schema)

    if validator.validate(data):
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'User already exists'}), 409
        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = User(name=data['name'], email=data['email'], password=hashed_password, admin=False)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!', 'user': user_schema.dump(new_user).data}), 201

    else:
        return jsonify({'message': 'User not created!', 'errors': validator.errors}), 400


@user_api.route('/api/v1/users/<user_id>', methods=['GET'])
@token_required
def get_one_user(current_user, user_id):
    """Devuelve la info de un usuario dado un user_id."""
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    return user_schema.jsonify(user)


@user_api.route('/api/v1/users/<user_id>', methods=['PUT'])
@token_required
@admin_required
def promote_user(current_user, user_id):
    """Convierte un usuario a administrador."""
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User promoted!'})


@user_api.route('/api/v1/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Elimina un usuario."""
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted!'})
