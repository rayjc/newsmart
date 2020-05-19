import logging
from functools import wraps

from flask import flash, g, jsonify, redirect, session

CURR_USER_KEY = "curr_user"


def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user. Flash logout message."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        flash("Logged out!", "success")


def login_required(redirect_url="/", isJSON=False):
    def _login_required(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not g.user:
                if isJSON:
                    return (
                        jsonify({"message": "Permission denied. Please log in."}),
                        401
                    )
                flash("Access unauthorized.", "danger")
                return redirect(redirect_url)

            # logged in;
            retval = function(*args, **kwargs)
            return retval
        return wrapper
    return _login_required


def new_logger(name="logger"):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s.py : %(funcName)s():%(lineno)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    
    return logger
