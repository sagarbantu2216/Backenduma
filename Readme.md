#create virtual env if required 
python -m venv your_venv_name

#activate the env
your_venv_name/scripts/activate


#required modules instalation
pip install -r requirements.txt


#create datbase and the user_db

CREATE DATABASE user_db;

USE user_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255)
);

#curl codes to test api


curl -X POST http://127.0.0.1:5000/signup \
-H "Content-Type: application/json" \
-d '{"name": "John Doe", "email": "johndoe@example.com", "password": "password123"}'



curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d '{"email": "johndoe@example.com", "password": "password123"}'

curl -X POST http://127.0.0.1:1000/lungpredict \
-F "user_id=1" \
-F "patient_name=John Doe" \
-F "patient_age=45" \
-F "patient_gender=Male" \
-F "patient_address=123 Main St" \
-F "patient_ct_image=@/path/to/ct_image.png"


curl -X GET http://127.0.0.1:1000/getAllData/1


