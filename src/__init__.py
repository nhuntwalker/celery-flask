"""."""
from flask import (
    Flask,
    request,
    render_template,
    session,
    flash,
    redirect,
    url_for,
    jsonify
)

from flask_mail import Mail, Message
from celery import Celery
import os
import random
import time


# start a new Flask app
app = Flask(__name__)

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

# from src import app
# from src.tasks import send_async_email, long_task

mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    """View for the home route."""
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    message_details = {
        "subject": "Hello from Flask",
        "recipients": [request.form['email']],
        "body": "This is a test email sent from a background Celery task."
    }

    # send the email
    if request.form['submit'] == 'Send':
        # send right away
        send_async_email.delay(message_details)
        flash('Sending email to {0}'.format(email))

    else:
        # send in one minute
        send_async_email.delay(message_details)
        flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('index'))


@app.route('/longtask', methods=['POST'])
def longtask():
    """View for a long task."""
    task = long_task.apply_async()  # returns a task object with certain properties
    return jsonify({}), 202, {
        'Location': url_for('taskstatus', task_id=task.id)
    }  # this looks like a redirect


@app.route('/status/<task_id>')
def taskstatus(task_id):
    """Update with task status for a given task."""
    task = long_task.AsyncResult(task_id)  # task is an instance of AsyncResult
    if task.state == "PENDING":
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "current": task.info.get('current', 0),
            "total": task.info.get('total', 1)
        }
        if "result" in task.info:
            response["result"] = task.info["result"]

    else:  # something went wrong in the background job
        response = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info)  # this is the exception raised
        }
    return jsonify(response)


# from src import celery, Message, app

@celery.task
def send_async_email(msg_details):
    """Background task to send an email with Flask-Mail."""

    with app.app_context():
        msg = Message(
            msg_details['subject'],
            msg_details['recipients'])
        msg.body = msg_details['body']
        mail.send(msg)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silence', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(
                random.choice(verb),
                random.choice(adjective),
                random.choice(noun)
            )

        # self.update_state is how celery receives task updates
        # used a custom state called "PROGRESS" with its own metadata
        self.update_state(state='PROGRESS', meta={'current': i, 'total': total, 'status': message})
        time.sleep(1)
    # return a serializable object that'll be attached to the "info" attribute
    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}
