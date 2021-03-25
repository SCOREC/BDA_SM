import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, session, url_for
)
from werkzeug.exceptions import abort

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    # do something with the user_id