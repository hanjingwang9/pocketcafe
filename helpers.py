import requests

from flask import redirect, render_template, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def fetch_image(drink_name):
    """Fetch reference image based on coffee name and brand"""

    # Locate Unsplash API URL
    url = f"https://api.unsplash.com/search/photos"

    # Set specific parameters and search
    params = {
        "query": f"{drink_name} coffee",
        "client_id": "Kp_HlNeeiPwleRTdpdH6ULD3KBhNoMZj_Sjj-s9cJ0g",
        "per_page": 1
    }
    response = requests.get(url, params=params)

    # If resulting image exists, return the image link
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            return results[0]["urls"]["regular"]
        
    # If not, return nothing
    return None


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function