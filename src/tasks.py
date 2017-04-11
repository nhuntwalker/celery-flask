"""Tasks for Celery to execute."""
from src import celery, Message, mail, app


@celery.task
def send_async_email(msg_details):
    """Background task to send an email with Flask-Mail."""
    msg = Message(
        msg_details['subject'],
        msg_details['recipients'])
    msg.body = msg_details['body']

    with app.app_context():
        mail.send(msg)
