import csv
import os
import urllib.request
import requests

from flask import redirect, render_template, request, session
from functools import wraps


def uhoh(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("uhoh.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# def exists(path):
#     """
#     Makes sure the image URL given is a real image.

#     https://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
#     """
#     r = requests.head(path)
#     return r.status_code == requests.codes.ok

def exists(site, path):
    """
    Makes sure the image URL given is a real image.

    https://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
    """
    conn = httplib.HTTPConnection(site)
    conn.request('HEAD', path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200