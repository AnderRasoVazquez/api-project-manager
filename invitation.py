from flask import Blueprint, jsonify
from model import Invitation, invitation_schema, invitations_schema, db, Project, User
from decorators import token_required


invitation_api = Blueprint('invitation_api', __name__)


@invitation_api.route('/api/v1/invitations', methods=['GET'])
@token_required
def get_all_invitations(current_user):
    """Devuelve todas las invitaciones pendientes al usuario."""
    invitations = current_user.invitations
    return jsonify({"invitations": invitations_schema.dump(invitations).data})


@invitation_api.route('/api/v1/invitations/<invitation_id>', methods=['GET'])
@token_required
def get_one_invitation(current_user, invitation_id):
    """Devuelve una invitacion."""
    invitation = Invitation.query.filter_by(invitation_id=invitation_id).first()

    if not invitation:
        return jsonify({'message': 'No project found!'}), 404

    if invitation.user_id != current_user.user_id:
        return jsonify({'message': 'You don\'t have permission to access this invitation!'}), 403

    return jsonify({"invitation": invitation_schema.dump(invitation).data})


@invitation_api.route('/api/v1/invitations/<invitation_id>/accept', methods=['PUT'])
@token_required
def accept_invitation(current_user, invitation_id):
    """Acepta una invitacion."""
    invitation = Invitation.query.filter_by(invitation_id=invitation_id).first()

    if not invitation:
        return jsonify({'message': 'No project found!'}), 404

    if invitation.user_id != current_user.user_id:
        return jsonify({'message': 'You don\'t have permission to access this invitation!'}), 403

    invitation.project.members.append(current_user)
    db.session.commit()
    return jsonify({'message': 'The invitation has been accepted!'})


@invitation_api.route('/api/v1/invitations/<invitation_id>/decline', methods=['PUT'])
@token_required
def cancel_invitation(current_user, invitation_id):
    """Cancela una invitacion."""
    invitation = Invitation.query.filter_by(invitation_id=invitation_id).first()

    if not invitation:
        return jsonify({'message': 'No invitation found!'}), 404

    if invitation.user_id != current_user.user_id:
        return jsonify({'message': 'You don\'t have permission to access this invitation!'}), 403

    db.session.delete(invitation)
    db.session.commit()
    return jsonify({'message': 'The invitation has been declined!'})


@invitation_api.route('/api/v1/projects/<project_id>/invite/<user_email>', methods=['PUT'])
@token_required
def create_invitation(current_user, project_id, user_email):
    """Crea una invitacion."""
    if current_user.email == user_email:
        return jsonify({'message': 'You can\'t invite yourself!'}), 403

    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({'message': 'No project found!'}), 404

    if current_user not in project.members:
        return jsonify({'message': 'You don\'t have permission to access that project!'}), 403

    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    invitation = Invitation(user_id=user.user_id, project_id=project_id)
    db.session.add(invitation)
    db.session.commit()
    # TODO conectar con el FCM para notificar al usuario
    return jsonify({"message": "Invitation created!"})
