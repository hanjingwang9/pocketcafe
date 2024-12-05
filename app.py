
import os
import pytz
import requests

from cs50 import SQL
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, fetch_image

# Configure application
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Link SQL database
db = SQL("sqlite:///cafe.db")

# Global dictionary of user's top drinks
top = {}

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Shows summary of user's log entries"""
    global top

    # Limit data to the most recent week
    one_week = datetime.now(pytz.timezone("US/Eastern")) - timedelta(weeks=1)

    # Retrieve data from database
    summary = db.execute("SELECT AVG(rating) as avg_rating, COUNT(*) AS total FROM logs WHERE user_id = ? AND date >= ?", 
                         session["user_id"], one_week)
    top = db.execute("SELECT name, roast, sweetness FROM logs WHERE user_id = ? AND date >= ? ORDER BY rating DESC, date DESC LIMIT 5", session["user_id"], one_week)
    
    # Render homepage
    return render_template("index.html", summary=summary, top=top,  username=session["username"])

@app.route("/entries")
@login_required
def entries():
    """Show full history of log entries"""
    # Get log entries based on user id
    entries = db.execute(
        "SELECT * FROM logs WHERE user_id = ?", session["user_id"])

    # Display history
    return render_template("entries.html", entries=entries, username=session["username"])


@app.route("/namecard")
@login_required
def namecard():
    """Allow user to create a customizable coffee namecard"""
    # Render namecard page with user information and top drinks 
    return render_template("namecard.html", top=top, username=session["username"])


@app.route("/log", methods=["GET", "POST"])
def log():
    """Document user's coffee log entries"""
    if request.method == "POST":
        # Get contents of log entry from submission
        name = request.form.get('name')
        brand = request.form.get('brand')
        roast = request.form.get('roast')
        sweetness = request.form.get('sweetness')
        rating = request.form.get('rating')
        description = request.form.get('description')
        
        # Ensure that all fields were filled out
        if not name or not brand or not roast or not sweetness or not description:
            return apology("must complete all required fields of log entry")
        
        # Document log entries in database
        db.execute("INSERT INTO logs (user_id, name, brand, roast, sweetness, rating, description, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   session["user_id"], name, brand, roast, sweetness, rating, description, datetime.now(pytz.timezone("US/Eastern")))
        
        # Redirect user to homepage
        flash("Successfully logged!")
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("log.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST
    if request.method == "POST":
        # Check if username is submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Check if password is submitted and matches
        if not request.form.get("password"):
            return apology("must provide password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Add user to database
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password)

            # Redirect user to homepage if username is unique
            flash("Successfully registered!")
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
            session["user_id"] = rows[0]["id"]
            session["username"] = rows[0]["username"]
            return redirect("/")
        
        # Return apology if username is not unique
        except Exception as e:
            return apology("username already exists")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for specified coffee drinks"""
    # User reached route via POST
    if request.method == "POST":
        # Retrieve user preferences
        brand = request.form.get("brand")
        espresso = request.form.get("espresso")
        temperature = request.form.get("temperature")
        keywords = request.form.get("keywords").strip()

        # Ensure that all required fields were completed
        if not brand or not espresso or not temperature:
            return apology("must complete all required fields")

        # If user did not enter a keyword, ensure it is a wildcard
        if not keywords:
            keywords = "%"
        else:
            keywords = f"%{keywords}%"

        # Initialize query with keywords
        query = "SELECT DISTINCT * FROM menu WHERE (name LIKE ? OR description LIKE ?)"
        params = [keywords, keywords]

        # Add additional constraints if user chose them
        if brand != "*":
            query += " AND brand = ?"
            params.append(brand)
        if espresso != "*":
            query += " AND espresso = ?"
            params.append(espresso)
        if temperature != "*":
            query += " AND (temperature = ? OR temperature = 0)"
            params.append(temperature)

        # Get results from menu database
        results = db.execute(query, *params)
        if not results:
            return apology("no drinks match your specifications")
        
        # Fetch an image for each keyword
        for result in results:
            result["image_url"] = fetch_image(result["name"])
            # Error handling if no image is returned
            if not result["image_url"]:
                result["image_url"] = "no-image"
        
        # Redirect user to results page
        return render_template("results.html", results=results)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else: 
        return render_template("search.html")