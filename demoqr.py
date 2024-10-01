import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import qrcode
import mysql.connector

app = Flask(__name__)

# Configure MySQL connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # replace with your MySQL username
        password="",  # replace with your MySQL password
        database="mh"
    )

# Generate QR code and save to file
def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

# Insert QR data and image path into the database
def add_to_database(qr_data, qr_image_path):
    connection = connect_db()
    cursor = connection.cursor()

    # Insert the QR code data and the image path into the database
    insert_query = "INSERT INTO qr_codes (qr_data, qr_image_path) VALUES (%s, %s)"
    cursor.execute(insert_query, (qr_data, qr_image_path))

    connection.commit()
    cursor.close()
    connection.close()

# Route for generating QR code
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        qr_data = request.form['qr_data']  # Get QR data from form input

        # File path for saving the generated QR code
        qr_filename = f"{qr_data}.png"
        qr_filepath = os.path.join('static', qr_filename)

        # Generate and save QR code
        generate_qr_code(qr_data, qr_filepath)

        # Add QR data and file path to the MySQL database
        add_to_database(qr_data, qr_filepath)

        # Redirect to download page
        return redirect(url_for('download_qr', filename=qr_filename))

    return render_template('index.html')

# Route for downloading the QR code image
@app.route('/download/<filename>')
def download_qr(filename):
    return send_file(os.path.join('static', filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
