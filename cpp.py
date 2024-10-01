import cv2
import numpy as np
import mysql.connector
from flask import Flask, request, jsonify, render_template
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mh"
)

# Load pre-trained Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    data = request.json['image']
    img_data = base64.b64decode(data.split(',')[1])
    img = Image.open(BytesIO(img_data)).convert('RGB')
    img_np = np.array(img)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Detect faces in the image
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Detect QR code in the image
    qr_detector = cv2.QRCodeDetector()
    qr_data, points, _ = qr_detector.detectAndDecode(img_cv)

    if len(faces) == 0 and not qr_data:
        return jsonify({"message": "No faces or QR codes detected."})

    # Check if QR data exists
    if qr_data:
        employee = identify_employee_by_qr(qr_data)
        if employee:
            return jsonify({"message": f"QR Detected: {employee}"})
        else:
            return jsonify({"message": "QR code not found in the database."})

    # Extract face region and search in database
    for (x, y, w, h) in faces:
        face = img_cv[y:y + h, x:x + w]
        employee = identify_employee_by_face(face)
        if employee:
            return jsonify({"message": f"Face Detected: {employee}"})
        else:
            return jsonify({"message": "Face not found in the database."})

def identify_employee_by_qr(qr_code):
    # Example SQL query to match QR data
    cursor = db.cursor()
    cursor.execute("SELECT name, id FROM employees WHERE qr_code=%s", (qr_code,))
    result = cursor.fetchone()

    if result:
        return f"Name: {result[0]}, ID: {result[1]}"
    else:
        return None

def identify_employee_by_face(face):
    # Example SQL query for face recognition
    # Use face encoding or face image comparison (you can use face_recognition library for better accuracy)
    cursor = db.cursor()
    cursor.execute("SELECT employee_name, employee_id FROM employees WHERE face_embedding=%s", (face,))
    result = cursor.fetchone()

    if result:
        return f"Name: {result[0]}, ID: {result[1]}"
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
