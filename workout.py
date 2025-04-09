from flask import request, jsonify, json, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import *


workout = Blueprint('workout', __name__)

@workout.post("/workout/uploadData")
@jwt_required()
def uploadData():
    data = request.get_json()
    current_user = int(get_jwt_identity())

    ##json_data = json.load(data)
    for sample in data['samples']:
        new_sample = WorkoutDataSample(workout_id=data['workout_id'],
                             user_id=current_user, 
                             sample_time=sample['sample_time'],
                             position_lat=sample['position_lat'],
                             position_lon=sample['position_lon'])
        
        db.session.add(new_sample)
    db.session.commit()
    return jsonify({'message': 'Samples added successfully'}), 201

@workout.post("/workout/createWorkout")
@jwt_required()
def createWorkout():
    data = request.get_json()
    current_user = int(get_jwt_identity())

    workout_name = data.get('workout_name')
    workout_start = data.get('workout_start')


    new_workout = Workout(workout_name=workout_name, workout_start=workout_start)
    db.session.add(new_workout)
    db.session.commit()

    new_participant = WorkoutParticipant(workout_id=new_workout.workout_id, user_id=current_user)
    db.session.add(new_participant)
    db.session.commit()
    return jsonify({'message': 'Workout created successfully'}), 201


@workout.get("/workout/getList")
@jwt_required()
def getWorkoutList():
    current_user = int(get_jwt_identity())
    workoutsList = Workout.query.join(Workout.participants).filter_by(user_id=current_user).all()
    return jsonify(workouts=[e.serialize() for e in workoutsList]), 201


@workout.get("/workout/getData")
@jwt_required()
def getWorkoutData():
    data = request.get_json()
    workout_id = data.get('workout_id')
    current_user = int(get_jwt_identity())
    sampleList = WorkoutDataSample.query.filter_by(workout_id=workout_id).all()
    return jsonify(samples=[e.serialize() for e in sampleList]), 201
    return