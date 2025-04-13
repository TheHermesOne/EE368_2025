from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

mysqlUser = 'scottts'
mysqlPass = 'Stella%400143'

app = Flask(__name__)
app.secret_key = 'gnbgjnbvgjnvfynbvfyjnvfkmnvghkm;09654'
app.config['SQLALCHEMY_DATABASE_URI'] = (f'mysql+mysqlconnector://{mysqlUser}:{mysqlPass}@localhost/flask_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

GOOGLE_CLIENT_ID = '901210299692-qhupsq33ni3ib8vknlm7v3vmvg2v7qg2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
REDIRECT_URI = "http://127.0.0.1:5000/callback/google"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Dev only!

import OauthApp.Frontend
import OauthApp.BackEnd

