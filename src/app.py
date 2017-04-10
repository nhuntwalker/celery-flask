"""."""
from flask import Flask
from celery import Celery

# start a new Flask app
app = Flask(__name__)

# set the location of the message broker
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

# sets the location of where results can be pulled from
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# initialize celery for this app, while setting the broker
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

# updates celery configuration with the rest of the app configuration
celery.conf.update(app.config)
