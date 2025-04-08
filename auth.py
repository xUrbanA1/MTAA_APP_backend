from flask import Flask, request, jsonify, Blueprint
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database import *
auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# register POST
# login POST
# getProfile
#
# changePassword
# changeUsername
# changeEmail
# changePhoto
#
# getFriendList
# addFriendRequest
# acceptRequest
# rejectRequest


@auth.post("/auth/register")
def createUser():
    data = request.get_json()
    user_name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    # user_photo = data.get('useloginr_photo')  # assuming it's passed as a base64 encoded string

    new_user = User(user_name=user_name, email=email,
                    password_hashed=password_hashed)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201


@auth.post("/auth/login")
def verifyLogin():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hashed.encode("utf-8"), password):
        access_token = create_access_token(identity=str(user.user_id))
        return jsonify({"token": access_token, "user_id": user.user_id})
    else:
        return jsonify({"msg": "Bad email or password"}), 401


@auth.get("/auth/getuser")
@jwt_required()
def get_user():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()
    return jsonify({"user_id": user.user_id, "user_name": user.user_name, "email": user.email})
