from flask import request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Generated using ChatGPT based on sql script
# Define the 'users' table
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True)
    password_hashed = db.Column(db.Text)
    user_photo = db.Column(db.LargeBinary)

    # Relationship to 'friend_list'
    friends = db.relationship('Friend', foreign_keys='Friend.user_id', backref='user', lazy=True)
    friends_of = db.relationship('Friend', foreign_keys='Friend.friend_id', backref='friend', lazy=True)

    def __repr__(self):
        return f'<User {self.user_name}>'

# Define the 'friend_list' table (many-to-many relationship between users)
class Friend(db.Model):
    __tablename__ = 'friend_list'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    accepted = db.Column(db.Boolean)

    def __repr__(self):
        return f'<Friend {self.user_id} - {self.friend_id}>'

# Define the 'workouts' table
class Workout(db.Model):
    __tablename__ = 'workouts'
    workout_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workout_name = db.Column(db.String(255))
    workout_start = db.Column(db.DateTime)

    # Relationship to 'workouts_participants'
    participants = db.relationship('WorkoutParticipant', backref='workout', lazy=True)

    def __repr__(self):
        return f'<Workout {self.workout_name}>'

    def serialize(self):
        return {
            'workout_id': self.workout_id, 
            'workout_name': self.workout_name,
            'workout_start': self.workout_start,
        }
    
# Define the 'workouts_participants' table
class WorkoutParticipant(db.Model):
    __tablename__ = 'workout_participants'
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    total_distance = db.Column(db.Float)
    avg_speed = db.Column(db.Float)
    max_speed = db.Column(db.Float)

    def __repr__(self):
        return f'<WorkoutParticipant {self.workout_id} - {self.user_id}>'
    
    def serialize(self):
        return {
            'workout_id': self.workout_id, 
            'user_id': self.user_id,
            'total_distance': self.total_distance,
            'avg_speed': self.avg_speed,
            'max_speed': self.max_speed,
        }

# Define the 'workout_data_sample' table
class WorkoutDataSample(db.Model):
    __tablename__ = 'workout_data_sample'
    sample_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sample_time = db.Column(db.DateTime)
    position_lat = db.Column(db.Float)
    position_lon = db.Column(db.Float)

    def __repr__(self):
        return f'<WorkoutDataSample {self.sample_id}>'
    
    def serialize(self):
        return {
            'sample_id': self.sample_id,
            'workout_id': self.workout_id, 
            'user_id': self.user_id,
            'sample_time': self.sample_time,
            'position_lat': self.position_lat,
            'position_lon': self.position_lon,
        }

# Define the 'workout_data_shared' table
class WorkoutDataShared(db.Model):
    __tablename__ = 'workout_data_shared'
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    shared_with = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<WorkoutDataShared {self.workout_id} - {self.user_id}>'

# Create tables in the database (run once to create the tables)
# @database.before_first_request
# def create_tables():
#     db.create_all()


def init_db(app):
    db.init_app(app)

database = Blueprint('database', __name__)