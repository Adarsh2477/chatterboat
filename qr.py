import cv2
import numpy as np
import mysql.connector
from flask import Flask, request, jsonify, render_template
import base64
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode  # Import pyzbar for decoding QR codes

app = Flask(__name__)

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Add your MySQL password
    database="mh"  # Your database name
)

# Function to decode QR from the image
def decode_qr(img):
    # Decode the QR code using pyzbar
    decoded_objects = decode(img)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')  # Return the decoded QR data
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_qr_image', methods=['POST'])
def upload_qr_image():
    try:
        data = request.json['image']
        img_data = base64.b64decode(data.split(',')[1])
        img = Image.open(BytesIO(img_data)).convert('RGB')
        img_np = np.array(img)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Resize the image for better QR detection
        img_resized = cv2.resize(img_cv, (400, 400), interpolation=cv2.INTER_LINEAR)

        # Convert to grayscale
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to improve QR detection
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

        # Detect and decode QR code
        qr_data = decode_qr(thresh)

        if qr_data:
            qr_data_cleaned = qr_data.strip()  # Clean QR data for matching
            employee = get_employee_by_qr(qr_data_cleaned)
            if employee:
                return jsonify({"success": True, "name": employee[0], "id": employee[1]})
            else:
                return jsonify({"success": False, "message": "QR code not found in the database."})
        else:
            return jsonify({"success": False, "message": "No QR code detected."})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while processing the image."})

# Function to fetch employee data based on the cleaned QR data
def get_employee_by_qr(qr_data):
    try:
        cursor = db.cursor()
        print(f"Decoded QR data: '{qr_data}'")  # Debugging: print the QR data being used in the query
        cursor.execute("SELECT employee_name, employee_id FROM employees WHERE qr_code = %s", (qr_data,))
        result = cursor.fetchone()
        print(f"Database Query Result: {result}")  # Debugging: print the result of the query
        
        if result:
            return result
        else:
            print(f"No result found for QR code: {qr_data}")
            return None
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None

# Route for employee details page
@app.route('/employee_details')
def employee_details():
    name = request.args.get('name')
    id = request.args.get('id')
    return render_template('employee_details.html', name=name, id=id)

if __name__ == '__main__':
    app.run(debug=True)
