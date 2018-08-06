from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager

# Setup flask app
app = Flask(__name__)

# Secret key is required for wt-forms (you can choose anything to be your secret key)
app.config['SECRET_KEY'] = '34987rh3o4fhwofn23490'

# Setup mail server (I am using gmail)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'Your gmail address goes here'
app.config['MAIL_PASSWORD'] = 'Your gmail address password goes here'
mail = Mail(app)

# SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite/signUp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup Database
db = SQLAlchemy(app)
db.init_app(app)

# Setup Bcrypt (used to hash user passwords)
bcrypt = Bcrypt(app)

# Setup login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Used to generate tokens when sending confirmation mails
serializer = URLSafeTimedSerializer('iou3bv4839201b3wiqbw')

from LoginDemoApp import main
