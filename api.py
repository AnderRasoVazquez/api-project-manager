from flask import Flask
from werkzeug.security import generate_password_hash
from login import login_api
from model import *
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


app.register_blueprint(project_api)
app.register_blueprint(task_api)
app.register_blueprint(login_api)
app.register_blueprint(user_api)


if __name__ == '__main__':
    app.run(debug=True)
