import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database import *
from auth import auth
from friends import friends
from workout import workout
import firebase_admin
from firebase_admin import credentials

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

app.register_blueprint(database)
app.register_blueprint(auth)
app.register_blueprint(friends)
app.register_blueprint(workout)

cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route("/")
def hello_world():
    return """<meta http-equiv="refresh" content="0; url=https://mtaaappbackend.docs.apiary.io/">"""
