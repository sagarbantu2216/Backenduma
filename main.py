import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt
from urllib.parse import quote_plus

# Initialize Flask app
app = Flask(__name__)

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

# Define the base and create a User model
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))

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

if __name__ == '__main__':
    app.run(debug=True,port=1000)
