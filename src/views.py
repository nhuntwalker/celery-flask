"""."""
from src import app
from src.tasks import send_async_email
from flask import request, render_template, session, flash, redirect, url_for


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
