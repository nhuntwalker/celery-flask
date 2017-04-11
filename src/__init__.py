"""."""
from flask import (
    Flask,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for
)
from flask_mail import Mail, Message
from celery import Celery
import os

# start a new Flask app
app = Flask(__name__)
mail = Mail(app)

# set the location of the message broker
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

# sets the location of where results can be pulled from
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# sets the secret key so that we can use the session on the request object
app.secret_key = os.environ.get('SECRET_KEY')

# initialize celery for this app, while setting the broker
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

# updates celery configuration with the rest of the app configuration
celery.conf.update(app.config)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

from src import views  # flask likes its view imports on the bottom
