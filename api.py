from flask import Flask, jsonify
from werkzeug.security import generate_password_hash
from model import *
from login import login_api
from project import project_api
from task import task_api
from user import user_api

# https://www.restapitutorial.com/httpstatuscodes.html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
# TODO change for postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_manager.db'


db.init_app(app)
ma.init_app(app)


def initial_setup():
    """Ejecutar desde la terminal para crear la base de datos y datos de prueba.
    import api
    api.initial_setup()
    """
    with app.app_context():
        db.create_all()
        add_initial_values()


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
    projectTwo = Project(name='User project', desc='Tareas para el user project')
    db.session.add(project)
    db.session.commit()

    task = Task(name="A task", project=project)
    db.session.add(task)
    db.session.commit()

    user.projects.append(project)
    user.projects.append(projectTwo)
    admin.projects.append(project)
    db.session.commit()
    return jsonify({'message': 'Initial values created!'})


app.register_blueprint(project_api)
app.register_blueprint(task_api)
app.register_blueprint(login_api)
app.register_blueprint(user_api)


if __name__ == '__main__':
    app.run(debug=True)