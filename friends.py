import io
from flask import request, jsonify, Blueprint, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from database import *

friends = Blueprint('friends', __name__)

# makeFriendRequest +
# notifyFriend
# getFriendRequests +
# getFriendList +
# acceptRequest +
# rejectRequest/removeFriend +
# getFriend +


@friends.post('/friends/request/create')
@jwt_required()
def make_friend_request():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()
    friend_email = request.json.get("email")
    if user.email == friend_email:
        return jsonify({"message": "User's own email entered"}), 409

    friend = User.query.filter_by(email=friend_email).first()

    if friend:
        if not Friend.query.filter_by(friend_id=user.user_id).first():
            friend_row = Friend(user_id=user.user_id,
                                friend_id=friend.user_id, accepted=False)
            db.session.add(friend_row)
            try:
                db.session.commit()
                return jsonify({"message": "Friend request made"}), 201
            except IntegrityError:
                return jsonify({"message": "Request made before or users already friends"}), 409
        else:
            return jsonify({"message": "Request made before or users already friends"}), 409
    else:
        return jsonify({"message": "User with entered email doesn't exist"}), 404


@friends.get('/friends/request/get')
@jwt_required()
def get_friend_requests():
    current_user = int(get_jwt_identity())
    friend_requests = Friend.query.filter_by(
        friend_id=current_user, accepted=False)
    return jsonify([{'user_id': friend.user_id, 'user_name': User.query.filter_by(user_id=friend.user_id).first().user_name, 'email': User.query.filter_by(user_id=friend.user_id).first().email} for friend in friend_requests])


@friends.patch('/friends/request/accept')
@jwt_required()
def accept_friend_request():
    current_user = int(get_jwt_identity())
    friend_id = int(request.json.get("friend_id"))
    friend_request = Friend.query.filter_by(user_id=friend_id,
                                            friend_id=current_user, accepted=False).first()
    if friend_request:
        friend_request.accepted = True
        db.session.commit()
        return jsonify({"message": "Friend request accepted"}), 201
    else:
        return jsonify({"message": "Friend request doesn't exist"}), 404


@friends.delete('/friends/request/reject')
@jwt_required()
def reject_friend_request():
    current_user = int(get_jwt_identity())
    friend_id = int(request.json.get("friend_id"))
    friend_request = Friend.query.filter_by(user_id=friend_id,
                                            friend_id=current_user, accepted=False).first()
    if friend_request:
        db.session.delete(friend_request)
        db.session.commit()
        return jsonify({"message": "Friend request removed"}), 200
    else:
        return jsonify({"message": "Friend request doesn't exist"}), 404


@friends.get('/friends/get')
@jwt_required()
def get_friends():
    current_user = int(get_jwt_identity())
    friend_list = []
    friends1 = Friend.query.filter_by(friend_id=current_user, accepted=True)
    friends2 = Friend.query.filter_by(user_id=current_user, accepted=True)
    for friend in friends1:
        friend_list.append(friend.user_id)
    for friend in friends2:
        friend_list.append(friend.friend_id)

    return jsonify([{'user_id': friend, 'user_name': User.query.filter_by(user_id=friend).first().user_name, 'email': User.query.filter_by(user_id=friend).first().email} for friend in friend_list])


@friends.delete('/friends/remove')
@jwt_required()
def remove_friend():
    current_user = int(get_jwt_identity())
    friend_id = int(request.json.get("friend_id"))
    friend = Friend.query.filter_by(user_id=friend_id,
                                    friend_id=current_user).first()
    if not friend:
        friend = Friend.query.filter_by(user_id=current_user,
                                        friend_id=friend_id).first()
    if friend:
        db.session.delete(friend)
        db.session.commit()
        return jsonify({"message": "Friend removed"}), 200
    else:
        return jsonify({"message": "Friend doesn't exist"}), 404


@friends.post("/friends/getuser")
@jwt_required()
def get_user():
    current_user = int(get_jwt_identity())
    friend_id = int(request.json.get("friend_id"))

    if Friend.query.filter_by(user_id=current_user, friend_id=friend_id).first() or Friend.query.filter_by(user_id=current_user, friend_id=friend_id).first():
        user = User.query.filter_by(user_id=friend_id).first()
        return jsonify({"user_id": user.user_id, "user_name": user.user_name, "email": user.email})
    else:
        return jsonify({"message": "User not in friends"}), 404


@friends.post("/friends/getphoto")
@jwt_required()
def get_photo():
    current_user = int(get_jwt_identity())
    friend_id = int(request.json.get("friend_id"))
    if Friend.query.filter_by(user_id=current_user, friend_id=friend_id).first() or Friend.query.filter_by(user_id=current_user, friend_id=friend_id).first():
        user = User.query.filter_by(user_id=friend_id).first()
        if user.user_photo:
            file_obj = io.BytesIO(user.user_photo)
        else:
            return jsonify({"error": "No profile picture provided"}), 404

        return send_file(
            file_obj,
            as_attachment=True,
            download_name="image.jpg",
            mimetype="image/jpg")
    else:
        return jsonify({"message": "User not in friends"}), 404
