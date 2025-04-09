import io
from flask import request, jsonify, Blueprint, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import *
auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# register +
# login +
# getProfile +
#
# changePassword +
# changeUsername +
# changePhoto +
# deleteUser +

@auth.post("/auth/register")
def createUser():
    data = request.get_json()
    user_name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_hashed = bcrypt.generate_password_hash(password).decode("utf-8")

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


@auth.patch('/user/change/username')
@jwt_required()
def update_user():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()
    new_username = request.json.get("username")
    user.user_name = new_username
    db.session.commit()
    return jsonify({"msg": "Username changed"}), 200


@auth.patch('/user/change/password')
@jwt_required()
def update_password():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()
    new_password = request.json.get("password")
    password_hashed = bcrypt.generate_password_hash(
        new_password).decode("utf-8")
    user.password_hashed = password_hashed
    db.session.commit()
    return jsonify({"msg": "Password changed"}), 200


@auth.patch('/user/change/photo')
@jwt_required()
def update_photo():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()

    file = request.data
    if not file:
        return jsonify({"error": "No file provided"}), 400

    user.user_photo = file
    db.session.commit()

    return jsonify({"msg": f"File uploaded successfully!"}), 201


@auth.get('/user/get/photo')
@jwt_required()
def get_photo():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()

    if user.user_photo:
        file_obj = io.BytesIO(user.user_photo)
    else:
        return jsonify({"error": "No profile picture provided"}), 404
        
    return send_file(
        file_obj,
        as_attachment=True,
        download_name="image.jpg",
        mimetype="image/jpg"
)


@auth.delete('/user/change/delete')
@jwt_required()
def delete_user():
    current_user = int(get_jwt_identity())
    user = User.query.filter_by(user_id=current_user).first()
    password = request.json.get("password", None)

    if user:
        if bcrypt.check_password_hash(user.password_hashed.encode("utf-8"), password):
            db.session.delete(user)
            db.session.commit()
            return jsonify({"error": "User deleted"}), 200
        else:
            return jsonify({"error": "Incorrect password"}), 401
    else:
        return jsonify({"error": "User doesn't exist"}), 401
    
