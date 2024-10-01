from flask import Flask, request, jsonify, send_file, render_template
import qrcode
import mysql.connector
import os

app = Flask(__name__)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="your_database"
)
cursor = db.cursor()

# Path to save QR codes
QR_FOLDER = 'qr_codes'
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

# Route to generate QR code for each employee and store it
@app.route('/generate_qr/<int:emp_id>', methods=['GET'])
def generate_qr(emp_id):
    # Fetch employee data based on emp_id
    cursor.execute("SELECT emp_id, emp_name FROM EMP WHERE emp_id = %s", (emp_id,))
    emp = cursor.fetchone()

    if emp:
        emp_id, emp_name = emp

        # Create QR code data (e.g., employee ID and name)
        qr_data = f"Employee ID: {emp_id}, Name: {emp_name}"

        # Generate QR code
        qr_code_img = qrcode.make(qr_data)
        qr_file_path = os.path.join(QR_FOLDER, f"emp_{emp_id}.png")
        qr_code_img.save(qr_file_path)

        # Store QR code data in the database
        cursor.execute("UPDATE EMP SET qr_code_data = %s WHERE emp_id = %s", (qr_data, emp_id))
        db.commit()

        # Provide a download link for the QR code
        return jsonify({
            'message': 'QR code generated successfully',
            'download_link': f"/download_qr/{emp_id}"
        })

    else:
        return jsonify({'error': 'Employee not found'}), 404

# Route to download the QR code
@app.route('/download_qr/<int:emp_id>', methods=['GET'])
def download_qr(emp_id):
    qr_file_path = os.path.join(QR_FOLDER, f"emp_{emp_id}.png")
    if os.path.exists(qr_file_path):
        return send_file(qr_file_path, as_attachment=True)
    else:
        return jsonify({'error': 'QR code not found'}), 404

# Route to scan QR code and display employee data
@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    qr_code_data = request.json.get('qr_data')

    # Fetch employee data using the scanned QR code data
    cursor.execute("SELECT emp_id, emp_name FROM EMP WHERE qr_code_data = %s", (qr_code_data,))
    emp = cursor.fetchone()

    if emp:
        emp_id, emp_name = emp
        return jsonify({
            'emp_id': emp_id,
            'emp_name': emp_name,
        })
    else:
        return jsonify({'error': 'Employee not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
