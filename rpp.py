from flask import Flask, render_template, Response
import cv2
import face_recognition
import numpy as np
import mysql.connector
import json

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="mh"  # Replace with your MySQL database name
)
cursor = db.cursor()

# Function to fetch known face encodings from the database
def get_known_faces():
    cursor.execute("SELECT name, face_encoding FROM faces")
    known_face_encodings = []
    known_face_names = []
    for (name, face_encoding_str) in cursor.fetchall():
        face_encoding = np.array(json.loads(face_encoding_str))
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)
    return known_face_encodings, known_face_names

# Function to generate video stream
def gen_frames():
    video_capture = cv2.VideoCapture(0)
    known_face_encodings, known_face_names = get_known_faces()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            # Draw box and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    video_capture.release()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Video stream route
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
