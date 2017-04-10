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
from flask_mail import Message, Mail
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


@celery.task
def send_async_email(msg_details):
    """Background task to send an email with Flask-Mail."""
    msg = Message(
        msg_details['subject'],
        msg_details['recipients'])
    msg.body = msg_details['body']

    with app.app_context():
        mail.send(msg)
