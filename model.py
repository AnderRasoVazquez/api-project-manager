from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from cerberus import Validator
import uuid
import datetime

db = SQLAlchemy()
ma = Marshmallow()


def _to_date(s):
    """Convierte un string a una fecha."""
    return datetime.datetime.strptime(s, '%Y-%m-%d')


def generate_uuid():
    """Genera un uuid"""
    return str(uuid.uuid4())


# Tabla para miembros de proyectos
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
    works = db.relationship('Work', backref=db.backref('user'))
    invitations = db.relationship('Invitation', backref=db.backref('user'))


_user_creation_schema = {
    'email': {'type': 'string', 'required': True, 'empty': False},
    'name': {'type': 'string', 'required': True, 'empty': False},
    'password': {'type': 'string', 'required': True, 'empty': False}
}
create_user_validator = Validator(_user_creation_schema)


class Project(db.Model):
    """Tabla proyectos de la base de datos."""
    project_id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))

    tasks = db.relationship('Task', backref=db.backref('project'))
    invitations = db.relationship('Invitation', backref=db.backref('project'))


_project_creation_schema = {
    'name': {'type': 'string', 'required': True, 'empty': False},
    'desc': {'type': 'string', 'empty': False}
}
create_project_validator = Validator(_project_creation_schema)

_project_update_schema = {
    'name': {'type': 'string', 'empty': False},
    'desc': {'type': 'string', 'empty': False}
}
update_project_validator = Validator(_project_update_schema)


class Task(db.Model):
    task_id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))
    due_date = db.Column(db.Date)
    init_date = db.Column(db.Date)
    expected = db.Column(db.Float(), default=0)
    progress = db.Column(db.Integer(), default=0)

    project_id = db.Column(db.String(50), db.ForeignKey('project.project_id'))
    works = db.relationship('Work', backref=db.backref('task'))


_task_creation_schema = {
    'name': {'type': 'string', 'required': True, 'empty': False},
    'desc': {'type': 'string', 'empty': False},
    'due_date': {'type': 'date', 'empty': False, 'coerce': _to_date},
    'init_date': {'type': 'date', 'empty': False, 'coerce': _to_date},
    'expected': {'type': 'float', 'empty': False, 'min': 0},
    'progress': {'type': 'integer', 'empty': False, 'min': 0, 'max': 100}
}
create_task_validator = Validator(_task_creation_schema)

_task_update_schema = {
    'name': {'type': 'string', 'empty': False},
    'desc': {'type': 'string', 'empty': False},
    'due_date': {'type': 'date', 'empty': False, 'coerce': _to_date},
    'init_date': {'type': 'date', 'empty': False, 'coerce': _to_date},
    'expected': {'type': 'float', 'empty': False, 'min': 0},
    'progress': {'type': 'integer', 'empty': False, 'min': 0, 'max': 100}
}
update_task_validator = Validator(_task_update_schema)


class Work(db.Model):
    work_id = db.Column(db.String, default=generate_uuid, nullable=False, unique=True)

    task_id = db.Column(db.String(50), db.ForeignKey('task.task_id'), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), primary_key=True)

    date = db.Column(db.Date, primary_key=True)
    time = db.Column(db.Float(), nullable=False)


_work_creation_schema = {
    'date': {'type': 'date', 'empty': False, 'coerce': _to_date, 'required': True},
    'time': {'type': 'float', 'empty': False, 'required': True}
}
create_work_validator = Validator(_work_creation_schema)

_work_update_schema = {
    'time': {'type': 'float', 'empty': False, 'required': True}
}
update_work_validator = Validator(_work_update_schema)


class Invitation(db.Model):
    """Tabla de datos de invitaciones. Si se acepta una invitacion se añade el usuario como miembro del proyecto."""
    # TODO igual es buena idea poner quien manda la invitacion del usuario
    invitation_id = db.Column(db.String, default=generate_uuid, nullable=False, unique=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), primary_key=True)
    project_id = db.Column(db.String(50), db.ForeignKey('project.project_id'), primary_key=True)


class UserSchema(ma.ModelSchema):
    """Esquema para la clase usuario."""

    class Meta:
        fields = ('user_id', 'name', 'email', 'admin', '_links')

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("user_api.get_one_user", user_id="<user_id>"),
         "collection": ma.URLFor("user_api.get_all_users")}
    )


class ProjectSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""

    class Meta:
        model = Project

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("project_api.get_one_project", project_id="<project_id>"),
         "collection": ma.URLFor("project_api.get_user_projects")}
    )


class TaskSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""

    class Meta:
        # TODO date
        # https://stackoverflow.com/questions/35795622/short-way-to-serialize-datetime-with-marshmallow
        model = Task

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("task_api.get_one_task", task_id="<task_id>"),
         "collection": ma.URLFor("task_api.get_all_tasks", project_id="<project_id>")}
    )


class WorkSchema(ma.ModelSchema):
    """Esquema para la clase proyectos."""

    class Meta:
        model = Work

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("work_api.get_one_work", work_id="<work_id>"),
         "collection": ma.URLFor("work_api.get_all_task_work", task_id="<task_id>")}
    )


class InvitationSchema(ma.ModelSchema):
    """Esquema para la clase de invitaciones."""

    class Meta:
        model = Invitation

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("invitation_api.get_one_invitation", invitation_id="<invitation_id>"),
         "collection": ma.URLFor("invitation_api.get_all_invitations")}
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
work_schema = WorkSchema()
works_schema = WorkSchema(many=True)
invitation_schema = InvitationSchema()
invitations_schema = InvitationSchema(many=True)
