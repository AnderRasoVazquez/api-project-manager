from flask import Flask, request, jsonify, make_response
from model import db, ma, User, Project, Task
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from cerberus import Validator
import uuid
import jwt
import datetime
import json
from project import project_api

# https://www.restapitutorial.com/httpstatuscodes.html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

# TODO change for postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_manager.db'

db.init_app(app)
ma.init_app(app)


# TODO ya se validar con cerberus, seria interesante serializarlo con marshmallow
def add_initial_values():
    """Añadir valores iniciales a la base de datos."""
    hashed_password = generate_password_hash('admin', method='sha256')
    admin = User(name='admin', email='admin', password=hashed_password, admin=True)
    db.session.add(admin)
    db.session.commit()

    hashed_password = generate_password_hash('user', method='sha256')
    user = User(name='user', email='user', password=hashed_password, admin=False)
    db.session.add(user)
    db.session.commit()

    project = Project(name='TFG', desc='Tareas para el TFG')
    db.session.add(project)
    db.session.commit()

    task = Task(name="A task", project=project)
    db.session.add(task)
    db.session.commit()

    user.projects.append(project)
    db.session.commit()


class UserSchema(ma.Schema):
    """Esquema para la clase usuario."""
    class Meta:
        fields = ('user_id', 'name', 'email', 'admin')


class TaskSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""
    class Meta:
        model = Task


user_schema = UserSchema()
users_schema = UserSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


app.register_blueprint(project_api)

def token_required(f):
    """Decorator para comprobar que el token es valido antes de ejecutar la funcion."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message': 'Wrong token!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator para comprobar que se es administrador antes de ejecutar la funcion."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.admin:
            return jsonify({'message': 'Cannot perform that function!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


# TODO
@app.route('/api/v1/tasks', methods=['GET'])
# @token_required
# @admin_required
# def get_all_tasks(current_user):
def get_all_tasks():
    """Devolver todas las tareas."""
    tasks = Task.query.all()
    output = tasks_schema.dump(tasks)
    return jsonify({"tasks": output.data})


# TODO
@app.route('/api/v1/projects', methods=['GET'])
# @token_required
# @admin_required
# def get_all_tasks(current_user):
def get_all_projects():
    """Devolver todos los proyectos."""
    projects = Project.query.all()
    output = projects_schema.dump(projects)
    return jsonify({"projects": output.data})


@app.route('/api/v1/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Devolver todos los usuarios."""
    users = User.query.all()
    output = users_schema.dump(users)
    return jsonify({"users": output.data})


@app.route('/api/v1/users', methods=['POST'])
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
        new_user = User(user_id=str(uuid.uuid4()), name=data['name'], email=data['email'], password=hashed_password, admin=False)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!', 'user': user_schema.dump(new_user).data}), 201

    else:
        return jsonify({'message': 'User not created!', 'errors': validator.errors}), 400


@app.route('/api/v1/users/<user_id>', methods=['GET'])
@token_required
def get_one_user(current_user, user_id):
    """Devuelve la info de un usuario dado un user_id."""
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    return user_schema.jsonify(user)


@app.route('/api/v1/users/<user_id>', methods=['PUT'])
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


@app.route('/api/v1/users/<user_id>', methods=['DELETE'])
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


def login_error():
    """Devuelve una respuesta indicando el error al intentar hacer login."""
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/api/v1/login')
def login():
    """Inicio de sesion. Devuelve un token para usarlo despues."""
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return login_error()

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return login_error()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'user_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    # pass no es correcto
    return login_error()


if __name__ == '__main__':
    app.run(debug=True)
