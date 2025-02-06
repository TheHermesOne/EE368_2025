import flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://scottts:Stella%400143@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Users(db.Model, flask.Flask):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __init__(self, app, first_name, last_name, email, password_hash):
        self.app = app
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash

with app.app_context():
    db.create_all()

def signup(first_name, last_name, email, password):
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        print(f"Email already registered: {email}")
    else:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(first_name=first_name, last_name=last_name, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        print(f"User {email} added with hashed password.")

def login(email, password):
    existing_user = Users.query.filter_by(email=email).first()

    if existing_user and bcrypt.check_password_hash(existing_user.password_hash, password):
        print({existing_user.first_name},{existing_user.last_name})
    else:
        print({existing_user.password_hash},{password})
        print("Login failed")

def get_email():
    with app.app_context():
        users = Users.query.all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.first_name} {user.last_name},  Email: {user.email}, Hashsed Password: {user.password_hash}")


def delete_user(email, password):
    # Query the user by email
    user_to_delete = Users.query.filter_by(email=email).first()

    if user_to_delete and bcrypt.check_password_hash(user_to_delete.password_hash, password):
        # Delete the user from the session
        db.session.delete(user_to_delete)
        db.session.commit()
        print(f"User with email {email} has been deleted.")
    else:
        print(f"No user found with email {email}.")

## TEST CALLS ##

with app.app_context():
    #login("Scottts@clarkson.edu", "Stella@0143")
    #signup("Trenton", "Scott", "Scottts@clarkson.edu", "Stella@0143")
    #delete_user("scottts@clarkson.edu")

    get_email()

## END OF TEST CALLS ##

## OLD TEST CODE ##




