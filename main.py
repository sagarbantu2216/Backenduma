import os
import numpy as np  # Import numpy here
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.hash import bcrypt
from urllib.parse import quote_plus
from flask_cors import CORS
from werkzeug.utils import secure_filename
from lungprediction import chestScanPrediction
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'  # Folder where uploaded files will be stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database connection details
db_user = "root"
db_password = quote_plus("Edven@3648")  # Encode special characters in the password
db_host = "localhost"
db_name = "user_db"

# SQLAlchemy Database URI
db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

# Set up the SQLAlchemy engine and session
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
session = Session()

# Define the base and create models
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))
    patients = relationship('Patient', back_populates='user')

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    address = Column(Text)
    ct_image_path = Column(Text)
    prediction_result = Column(Text)
    prediction_image_path = Column(Text)
    time = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='patients')

# Create tables if they don't exist
Base.metadata.create_all(engine)

# API to sign up a new user
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    hashed_password = bcrypt.hash(password)

    # Check if the user already exists
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    # Create and add the new user
    new_user = User(name=name, email=email, password_hash=hashed_password)
    session.add(new_user)
    session.commit()

    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201

# API to login a user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    # Find user by email
    user = session.query(User).filter_by(email=email).first()

    if user and bcrypt.verify(password, user.password_hash):
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401
    
# Lung Cancer Prediction route
@app.route('/lungpredict', methods=["POST"])
def lungpredict():
    user_id = request.form.get('user_id')
    patient_name = request.form.get('patient_name')
    patient_age = request.form.get('patient_age')
    patient_gender = request.form.get('patient_gender')
    patient_address = request.form.get('patient_address')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if user exists
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User does not exist'}), 400

    # Check if the file is in the request
    if 'patient_ct_image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    f = request.files['patient_ct_image']

    # Save the uploaded image file to the UPLOAD_FOLDER
    filename = secure_filename(f.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(file_path)
    
    # Call the lung cancer prediction function using the saved file path
    prediction_image_path, prediction_result = chestScanPrediction(file_path)

    # Assuming chestScanPrediction returns (label, probabilities)
    label = prediction_result[0]  # First part of the result is the predicted label
    probabilities = prediction_result[1]  # Second part is the ndarray of probabilities

    # Ensure probabilities are converted to a list for JSON serialization
    if isinstance(probabilities, np.ndarray):
        probabilities = probabilities.tolist()

    # Create new patient record in the database
    new_patient = Patient(
        name=patient_name,
        age=int(patient_age),
        gender=patient_gender,
        address=patient_address,
        ct_image_path=file_path,  # Store the saved file path
        prediction_result=label,  # Store the prediction label
        prediction_image_path=prediction_image_path,  # Store the image path of the predicted result
        time=time,
        user_id=user.id  # Link the patient record to the logged-in user
    )

    session.add(new_patient)
    session.commit()

    # Return JSON response
    return jsonify({
        'message': 'Prediction completed and data saved.',
        'prediction': label,  # Predicted label
        'probabilities': probabilities,  # Probability values converted to list
        'image_path': prediction_image_path
    }), 200
    
# API to get all patient data by user ID
@app.route('/getAllData/<int:user_id>', methods=['GET'])
def get_all_data(user_id):
    # Check if the user exists
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get all patients under the user
    patients = session.query(Patient).filter_by(user_id=user_id).all()

    # Return the patient data
    patient_data = []
    for patient in patients:
        patient_data.append({
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_age': patient.age,
            'patient_gender': patient.gender,
            'patient_address': patient.address,
            'time': patient.time,
            'ct_image_path': patient.ct_image_path,
            'prediction_result': patient.prediction_result,
            'prediction_image_path': patient.prediction_image_path
        })

    return jsonify({'user_id': user.id, 'patients': patient_data}), 200

if __name__ == '__main__':
    app.run(debug=True, port=1000)
