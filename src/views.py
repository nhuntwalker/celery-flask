"""."""
from .app import app
from flask import (
    render_template,
    request,
    session
)


@app.route('/', methods=['GET', 'POST'])
def index():
    """View for the home route."""
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
