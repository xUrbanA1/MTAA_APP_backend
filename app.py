import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database import *
from auth import auth
from friends import friends
from workout import workout

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

app.register_blueprint(database)
app.register_blueprint(auth)
app.register_blueprint(friends)
app.register_blueprint(workout)

app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.get("/dbtest")
@jwt_required()
def dbtest():
    users = User.query.all()
    return jsonify([{'user_id': user.user_id, 'user_name': user.user_name, 'email': user.email} for user in users])
