# add_face.py
import cv2
import face_recognition
import numpy as np
import mysql.connector
import json

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",     # Replace with your MySQL username
    password="",     # Replace with your MySQL password
    database="mh"    # Replace with your MySQL database name
)
cursor = db.cursor()

# Function to check if face already exists in the database
def is_face_known(face_encoding):
    cursor.execute("SELECT face_encoding FROM faces")
    for (face_encoding_str,) in cursor.fetchall():
        known_encoding = np.array(json.loads(face_encoding_str))
        matches = face_recognition.compare_faces([known_encoding], face_encoding)
        if matches[0]:
            return True  # Face already exists
    return False

# Function to add new face encoding to the database if not already present
def add_new_face(name):
    # Capture video stream from the webcam
    video_capture = cv2.VideoCapture(0)
    
    print(f"Capturing face data for {name}. Look at the camera.")
    while True:
        ret, frame = video_capture.read()
        
        if not ret:
            print("Error: Unable to capture video.")
            break
        
        # Convert BGR image to RGB for face_recognition
        rgb_frame = frame[:, :, ::-1]
        
        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if face_encodings:
            print(f"Found {len(face_locations)} face(s). Capturing face data...")

            # Get the first face encoding (assuming one face per frame)
            face_encoding = face_encodings[0]

            # Check if the face is already in the database
            if is_face_known(face_encoding):
                print("Face is already in the database, skipping...")
            else:
                # Save face encoding and name to MySQL database
                face_encoding_str = json.dumps(face_encoding.tolist())  # Convert numpy array to list, then string
                sql = "INSERT INTO faces (name, face_encoding) VALUES (%s, %s)"
                cursor.execute(sql, (name, face_encoding_str))
                db.commit()
                print(f"Face data for {name} stored in the database.")
            
            break  # Stop after capturing and processing one face

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Example usage: Add a new face
if __name__ == "__main__":
    name = input("Enter the name of the person: ")
    add_new_face(name)
