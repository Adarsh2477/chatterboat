import os
import pickle
import mysql.connector
from deepface import DeepFace

# Step 1: Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mh"
)
cursor = conn.cursor()

# Step 2: Path to the single image
image_path = 'C:\\Users\\adarsh\\OneDrive\\Desktop\\catter boat\\adars.jpg'

# Extract employee info
employee_name = "Adarsh Kumar"
employee_id = "EMP001"

# Step 3: Extract face embedding using DeepFace, with enforce_detection set to False
embedding = DeepFace.represent(image_path, model_name="Facenet", enforce_detection=False)[0]["embedding"]

# Convert the embedding to binary format using pickle
embedding_blob = pickle.dumps(embedding)

# Step 4: Insert the employee data with face embedding into the MySQL database
sql_query = """
INSERT INTO employees (employee_name, employee_id, face_embedding) 
VALUES (%s, %s, %s)
"""

# Execute the insert query
cursor.execute(sql_query, (employee_name, employee_id, embedding_blob))

# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()

print("Data inserted successfully!")
