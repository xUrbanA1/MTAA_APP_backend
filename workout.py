from flask import request, jsonify, json, Blueprint
from flask_sock import Sock
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import *
from datetime import datetime


workout = Blueprint('workout', __name__)
sock = Sock(workout)

@workout.post("/workout/uploadData")
@jwt_required()
def uploadData():
    data = request.get_json()
    current_user = int(get_jwt_identity())
    workout_id=data['workout_id']

    if(type(workout_id) != int):
        return jsonify({'message': "Wrong data type"}), 400

    if (Workout.query.filter_by(workout_id=workout_id).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
        
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Unauthorized access"}), 403
    
    for sample in data['samples']:
        sample_time = sample['sample_time']
        position_lat=sample['position_lat']
        position_lon=sample['position_lon']

        if(type(position_lat) != float or position_lat > 180 or position_lat < -180 or type(position_lon) == float or position_lon > 180 or position_lon < -180 or type(sample_time) != str):
            continue
        try:
            datetime.strptime(sample_time, "%d-%m-%Y %H:%M:%S")
        except:
            continue
        
        new_sample = WorkoutDataSample(workout_id=workout_id,
                             user_id=current_user, 
                             sample_time=sample_time,
                             position_lat=position_lat,
                             position_lon=position_lon)
        
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

    if(type(workout_name) != str or len(workout_name) == 0 or type(workout_start) != str):
        return jsonify({'message': "Wrong data type"}), 400
    try:
        datetime.strptime(workout_start, "%d-%m-%Y %H:%M:%S")
    except:
        return jsonify({'message': "Wrong data type"}), 400

    new_workout = Workout(workout_name=workout_name, workout_start=workout_start)
    db.session.add(new_workout)
    db.session.commit()

    new_participant = WorkoutParticipant(workout_id=new_workout.workout_id, user_id=current_user)
    db.session.add(new_participant)
    db.session.commit()
    return jsonify({'message': 'Workout created successfully'}), 201

@workout.put("/workout/addParticipant")
@jwt_required()
def addParticipant():
    data = request.get_json()
    current_user = int(get_jwt_identity())

    workout_id = data.get('workout_id')
    participant_id = data.get('participant_id')

    
    if(type(participant_id) != int or type(workout_id) != int or type(current_user) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if(User.query.filter_by(user_id=participant_id).count()==0):
        return jsonify({'message': "User doesn't exist"}), 404
    
    if(Friend.query.filter_by(user_id=current_user, friend_id=participant_id, accepted=True).count()==0):
        return jsonify({'message': "New participant is not a friend"}), 403
    
    if (Workout.query.filter_by(workout_id=workout_id).count() or WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() != 0):
        new_participant = WorkoutParticipant(workout_id=workout_id, user_id=participant_id)
        db.session.add(new_participant)
        db.session.commit()
        return
    return


@workout.get("/workout/getList")
@jwt_required()
def getWorkoutList():
    current_user = int(get_jwt_identity())

    workoutsList = Workout.query.join(Workout.participants).filter_by(user_id=current_user).all()
    return jsonify(workouts=[e.serialize() for e in workoutsList]), 200


@workout.get("/workout/getData")
@jwt_required()
def getWorkoutData():
    data = request.get_json()
    workout_id = data.get('workout_id')
    current_user = int(get_jwt_identity())
    from_sample = data.get("from_sample")

    if (from_sample == None):
        from_sample = 0

    if(type(from_sample) != int or type(workout_id) != int or type(current_user) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if (Workout.query.filter_by(workout_id=workout_id).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
        
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0 and  WorkoutDataShared.query.filter_by(workout_id=workout_id, shared_with=current_user).count() != 0):
        return jsonify({'message': "Unauthorized access"}), 403
    
    sampleList = WorkoutDataSample.query.filter_by(WorkoutDataSample.sample_id >= from_sample, workout_id=workout_id).all()
    return jsonify(samples=[e.serialize() for e in sampleList]), 200

@workout.delete("/workout/deleteWorkout")
@jwt_required()
def deleteWorkout():
    data = request.get_json()
    workout_id = data.get('workout_id')
    current_user = int(get_jwt_identity())
    
    if(type(workout_id) != int or type(current_user) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if (WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
    
    WorkoutDataSample.query.filter_by(workout_id=workout_id, user_id=current_user).delete()
    WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).delete()

    if(WorkoutParticipant.query.filter_by(workout_id=workout_id).count() == 0):
        Workout.query.filter_by(workout_id=workout_id).delete()
    return  jsonify({'message': "Workout deleted successfully"}), 200

@workout.put("/workout/shareWorkout")
@jwt_required()
def shareWorkoutPut():
    data = request.get_json()
    workout_id = data.get('workout_id')
    shared_user_id = data.get('shared_user_id')
    current_user = int(get_jwt_identity())
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400

    if(WorkoutDataShared.query.filter_by(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id).count() != 0):
        return jsonify({'message': "Workout is alredy shared"}), 200

    sharedWorkout = WorkoutDataShared(workout_id, current_user, shared_user_id)
    db.session.add(sharedWorkout)
    db.session.commit()
    return jsonify({'message': "Workout shared successfully"}), 200



@workout.delete("/workout/unshareWorkout")
@jwt_required()
def shareWorkoutDelete():
    data = request.get_json()
    workout_id = data.get('workout_id')
    shared_user_id = data.get('shared_user_id')
    current_user = int(get_jwt_identity())
    
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400

    if(WorkoutDataShared.query.filter_by(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id).count() == 0):
        return jsonify({'message': "Workout isn't shared"}), 200
    
    WorkoutDataShared.query.filter_by(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id).delete()
    return jsonify({'message': "Workout unshared successfully"}), 200

@sock.route('/workout/WorkoutSocket')
@jwt_required()
def sockTest(ws):
    current_user = int(get_jwt_identity())
    while True:
        text = ws.receive()
        data = json.load(text)
        workout_id = data['workout_id']
        last_id = data['load_from']
        
        if (Workout.query.filter_by(workout_id=workout_id).count() or WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() != 0):
            for sample in data['samples']:
                new_sample = WorkoutDataSample(workout_id=workout_id,
                                    user_id=current_user, 
                                    sample_time=sample['sample_time'],
                                    position_lat=sample['position_lat'],
                                    position_lon=sample['position_lon'])
                
                db.session.add(new_sample)
            db.session.commit()

            sampleList = WorkoutDataSample.query.filter(WorkoutDataSample.sample_id >= last_id, WorkoutDataSample.user_id != current_user, workout_id=workout_id).all()
            ws.send(jsonify(samples=[e.serialize() for e in sampleList]))

