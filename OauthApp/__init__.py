from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

mysqlUser = 'lamontad'
mysqlPass = 'Whateves28!'

app = Flask(__name__)
app.secret_key = 'gnbgjnbvgjnvfynbvfyjnvfkmnvghkm;09654'
app.config['SQLALCHEMY_DATABASE_URI'] = (f'mysql+mysqlconnector://{mysqlUser}:{mysqlPass}@localhost/flask_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

import OauthApp.Frontend
import OauthApp.BackEnd

