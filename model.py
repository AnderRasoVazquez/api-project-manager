from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import uuid

db = SQLAlchemy()
ma = Marshmallow()


def generate_uuid():
    """Genera un uuid"""
    return str(uuid.uuid4())


project_member = db.Table('project_member',
                          db.Column('user_id', db.String(50), db.ForeignKey('user.user_id'), primary_key=True),
                          db.Column('project_id', db.String(50), db.ForeignKey('project.project_id'), primary_key=True)
                          )


class User(db.Model):
    """Tabla usuarios de la base de datos."""
    user_id = db.Column(db.String(50), unique=True, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(80), nullable=False)
    admin = db.Column(db.Boolean, default=False)

    projects = db.relationship('Project', secondary=project_member, backref=db.backref('members'))


class Project(db.Model):
    """Tabla proyectos de la base de datos."""
    project_id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))

    tasks = db.relationship('Task', backref=db.backref('project'))


class Task(db.Model):
    task_id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))
    due_date = db.Column(db.Date)
    init_date = db.Column(db.Date)
    expected = db.Column(db.Float(), default=0)
    progress = db.Column(db.Integer(), default=0)

    project_id = db.Column(db.String(50), db.ForeignKey('project.project_id'))


class UserSchema(ma.Schema):
    """Esquema para la clase usuario."""
    class Meta:
        fields = ('user_id', 'name', 'email', 'admin')


class ProjectSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""
    class Meta:
        model = Project


class TaskSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""
    class Meta:
        model = Task


user_schema = UserSchema()
users_schema = UserSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
