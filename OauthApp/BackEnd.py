from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from OauthApp import app


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://scottts:Stella%400143@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = Users(first_name=data['first_name'], last_name=data['last_name'], email=data['email'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = Users.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=True)
