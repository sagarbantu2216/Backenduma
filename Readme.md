create virtual env if required 
python -m venv your env name

activate the env
scripts/bin/activate

required modules
pip install sqlalchemy pymysql
pip install cryptography
pip insttall flask
pip install passlib
pip install bcrypt==3.1.7



create datbase and the user_db

CREATE DATABASE user_db;

USE user_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255)
);

curl codes to test api


curl -X POST http://127.0.0.1:5000/signup \
-H "Content-Type: application/json" \
-d '{"name": "John Doe", "email": "johndoe@example.com", "password": "password123"}'



curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d '{"email": "johndoe@example.com", "password": "password123"}'

