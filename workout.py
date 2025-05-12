from flask import request, jsonify, Blueprint
from flask_sock import Sock
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import *
from datetime import datetime
import jwt as pyjwt
import os
import json


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

    if (Workout.query.filter_by(workout_id=workout_id).count() == 0 or WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
    
    for sample in data['samples']:
        sample_time = sample['sample_time']
        position_lat=sample['position_lat']
        position_lon=sample['position_lon']

        if(type(position_lat) != float or position_lat > 180 or position_lat < -180 or type(position_lon) != float or position_lon > 180 or position_lon < -180 or type(sample_time) != str):
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
    return jsonify({'message': 'Workout created successfully', "workout_id": new_workout.workout_id}), 201

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
    
    if (Workout.query.filter_by(workout_id=workout_id).count() == 0 or WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 404

    if (WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=participant_id).count() != 0):
        return jsonify({'message': "Participant already exist"}), 403
    
    new_participant = WorkoutParticipant(workout_id=workout_id, user_id=participant_id)
    db.session.add(new_participant)
    db.session.commit()
    return jsonify({'message': "Participant added succefully"}), 201

@workout.put("/workout/updateParticipantData")
@jwt_required()
def updateParticipantData():
    data = request.get_json()
    current_user = int(get_jwt_identity())

    workout_id = data.get('workout_id')
    total_distance = data.get('total_distance')
    avg_speed = data.get('avg_speed')
    max_speed = data.get('max_speed')

    if(type(workout_id) != int or type(current_user) != int or (type(total_distance) != int and type(total_distance) != float and total_distance != None) or (type(avg_speed) != int and type(avg_speed) != float and avg_speed != None) or (type(max_speed) != int and type(max_speed) != float and max_speed != None)):
        return jsonify({'message': "Wrong data type"}), 400
    
    if (Workout.query.filter_by(workout_id=workout_id).count() == 0 or WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 404
    
    workoutParticipant = WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).first()
    if (total_distance != None):
        workoutParticipant.total_distance = total_distance
    if (avg_speed != None):
        workoutParticipant.avg_speed = avg_speed
    if (max_speed != None):
        workoutParticipant.max_speed = max_speed
        
    db.session.commit()
    return jsonify({'message': "Participant updated succefully"}), 200
    
@workout.get("/workout/getList")
@jwt_required()
def getWorkoutList():
    current_user = int(get_jwt_identity())

    workoutsList = db.session.query(Workout,WorkoutParticipant).join(WorkoutParticipant).filter(WorkoutParticipant.user_id==current_user).all()
    return jsonify(workouts=[WorkoutsListSerialize(e) for e in workoutsList]), 200

def WorkoutsListSerialize(self):
    return {
            'workout_id': self[0].workout_id, 
            'workout_name': self[0].workout_name,
            'workout_start': self[0].workout_start.isoformat(),
            'user_id': self[1].user_id,
            'total_distance': self[1].total_distance,
            'avg_speed': self[1].avg_speed,
            'max_speed': self[1].max_speed,
    }


@workout.get("/workout/getData/<workout_id>:<from_sample>")
@jwt_required()
def getWorkoutData(workout_id, from_sample):
    #data = request.get_json()
    workout_id = int(workout_id)
    from_sample = int(from_sample)
    current_user = int(get_jwt_identity())
    #from_sample = data.get("from_sample")

    if (from_sample == None):
        from_sample = 0

    if(type(from_sample) != int or type(workout_id) != int or type(current_user) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if (Workout.query.filter_by(workout_id=workout_id).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
        
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0 and  WorkoutDataShared.query.filter_by(workout_id=workout_id, shared_with=current_user).count() != 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
    
    sampleList = WorkoutDataSample.query.filter(WorkoutDataSample.sample_id >= from_sample, WorkoutDataSample.workout_id==workout_id).all()
    return jsonify(samples=[e.serialize() for e in sampleList]), 200

@workout.delete("/workout/deleteWorkout/<workout_id>")
@jwt_required()
def deleteWorkout(workout_id):
    #data = request.get_json()
    #workout_id = data.get('workout_id')
    workout_id = int(workout_id)
    current_user = int(get_jwt_identity())
    
    if(type(workout_id) != int or type(current_user) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if (WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400
    
    WorkoutDataSample.query.filter_by(workout_id=workout_id, user_id=current_user).delete()
    WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).delete()

    if(WorkoutParticipant.query.filter_by(workout_id=workout_id).count() == 0):
        Workout.query.filter_by(workout_id=workout_id).delete()
    db.session.commit()
    return  jsonify({'message': "Workout deleted successfully"}), 200

@workout.put("/workout/shareWorkout")
@jwt_required()
def shareWorkoutPut():
    data = request.get_json()
    workout_id = data.get('workout_id')
    shared_user_id = data.get('shared_user_id')
    current_user = int(get_jwt_identity())

    if(type(workout_id) != int or type(shared_user_id) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400

    if(WorkoutDataShared.query.filter_by(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id).count() != 0):
        return jsonify({'message': "Workout is alredy shared"}), 200

    sharedWorkout = WorkoutDataShared(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id)
    db.session.add(sharedWorkout)
    db.session.commit()
    return jsonify({'message': "Workout shared successfully"}), 200



@workout.delete("/workout/unshareWorkout/<workout_id>:<shared_user_id>")
@jwt_required()
def shareWorkoutDelete(workout_id,shared_user_id):
    #data = request.get_json()
    #workout_id = data.get('workout_id')x
    #shared_user_id = data.get('shared_user_id')
    workout_id = int(workout_id)
    shared_user_id = int(shared_user_id)
    current_user = int(get_jwt_identity())
    
    if(type(workout_id) != int or type(shared_user_id) != int):
        return jsonify({'message': "Wrong data type"}), 400
    
    if(WorkoutParticipant.query.filter_by(workout_id=workout_id, user_id=current_user).count() == 0):
        return jsonify({'message': "Workout doesn't exist"}), 400

    if(WorkoutDataShared.query.filter_by(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id).count() == 0):
        return jsonify({'message': "Workout isn't shared"}), 200
    
    WorkoutDataShared.query.filter_by(workout_id=workout_id, user_id=current_user, shared_with=shared_user_id).delete()
    db.session.commit()
    return jsonify({'message': "Workout unshared successfully"}), 200

@sock.route('/workout/socket')
def sockTest(ws):
    token = request.args.get("token")
    if not token:
        ws.send("Missing token")
        ws.close()
        return
    try:
        decoded = pyjwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
        user_identity = decoded["sub"]
    except pyjwt.ExpiredSignatureError:
        ws.send("Token expired")
        ws.close()
    except pyjwt.InvalidTokenError:
        ws.send("Invalid token")
        ws.close()
        
    current_user = user_identity
    while True:
        text = ws.receive()
        data = json.loads(text)
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

        sampleList = WorkoutDataSample.query.filter(WorkoutDataSample.sample_id >= last_id, WorkoutDataSample.user_id != current_user, WorkoutDataSample.workout_id == workout_id).all()
        #sampleList = WorkoutDataSample.query.filter(WorkoutDataSample.sample_id >= last_id, WorkoutDataSample.workout_id==workout_id).all()
        samplesReturn=[e.serialize() for e in sampleList]
        ws.send(json.dumps({"samples": samplesReturn}))
            
        

