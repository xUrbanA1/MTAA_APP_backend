CREATE TABLE users(
	user_id SERIAL PRIMARY KEY,
	user_name VARCHAR(50),
	email VARCHAR(255) UNIQUE,
	password_hashed TEXT,
	user_photo BYTEA,
	push_token VARCHAR(255)
);

CREATE TABLE friend_list(
	user_id INTEGER,
	friend_id INTEGER,
	accepted BOOLEAN,
	PRIMARY KEY (user_id, friend_id),
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (friend_id) REFERENCES users(user_id) ON DELETE CASCADE	
);

CREATE TABLE workouts(
	workout_id SERIAL PRIMARY KEY,
	workout_name VARCHAR(255),
	workout_start TIMESTAMP
);

CREATE TABLE workout_participants(
	workout_id INTEGER,
	user_id INTEGER,
	total_distance FLOAT,
	avg_speed FLOAT,
	max_speed FLOAT,
	PRIMARY KEY (workout_id, user_id),
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (workout_id) REFERENCES workouts(workout_id) ON DELETE CASCADE
);

CREATE TABLE workout_data_sample(
	sample_id SERIAL,
	workout_id INTEGER,
	user_id INTEGER,
	sample_time TIMESTAMP,
	position_lat FLOAT,
	position_lon FLOAT,
	PRIMARY KEY (sample_id, workout_id),
	FOREIGN KEY (workout_id) REFERENCES workouts(workout_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE workout_data_shared(
	workout_id INTEGER PRIMARY KEY,
	user_id INTEGER,
	shared_with INTEGER,
	FOREIGN KEY (workout_id) REFERENCES workouts(workout_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (shared_with) REFERENCES users(user_id) ON DELETE CASCADE
)