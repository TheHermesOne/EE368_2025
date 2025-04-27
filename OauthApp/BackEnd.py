from flask import Flask, request, jsonify, make_response

from OauthApp import *
import re


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=True)
    oauth_token = db.Column(db.String(500), nullable=True)  # Store GitHub/Google token

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error {e}")

def validate_password(password):

    if len(password) < 12:
        return False, "Password must be at least 12 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    password = data['password']
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return jsonify({"message": error_message}), 400

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
        return make_response({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'userID': user.id
    },200)
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/changePassword', methods=['POST'])
def change_password():
    data = request.json
    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:

        password = data['password']
        is_valid, error_message = validate_password(password)
        if not is_valid:
            return jsonify({"message": error_message}), 400

        #if valid password, hash and save
        existing_user.password_hash= bcrypt.generate_password_hash(data['password']).decode('utf-8')
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    else:
        return jsonify({"message": "No Email registered"}), 400

@app.route('/api/oauth_login', methods=['POST'])
def oauth_login():
    data = request.json
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    oauth_token = data['oauth_token']

    user = Users.query.filter_by(email=email).first()

    if user:
        # If user exists, optionally update their OAuth token
        user.oauth_token = oauth_token
    else:
        # Create a new user
        new_user = Users(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=None,  # No password for OAuth users
            oauth_token=oauth_token
        )
        db.session.add(new_user)

    db.session.commit()
    return jsonify({"message": "OAuth user saved successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
