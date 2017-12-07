from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import uhoh, login_required

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fresh.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and nickname were submitted
        if not request.form.get("username") or not request.form.get("nickname"):
            return uhoh("missing username or nickname", 400)

        # Initiate correct PAF code
        pafcode = "Fre5h50!"

        # Ensure PAF code was submitted and is correct
        if request.form.get("pafcode") != pafcode:
            return uhoh("PAF code is missing or incorrect", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return uhoh("missing password", 400)

        # Ensure password confirmation was submitted and matches password
        elif request.form.get("password") != request.form.get("confirmation"):
            return uhoh("confirmation either wasn't submitted or doesn't match password", 400)

        # Add user to database
        id = db.execute("INSERT INTO users (username, hash, nickname) VALUES(:username, :hash, :nickname)",
                        username=request.form.get("username"),
                        hash=generate_password_hash(request.form.get("password")),
                        nickname=request.form.get("nickname"))
        if not id:
            return uhoh("username or nickname taken", 400)

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("username") or not request.form.get("password"):
            return uhoh("must provide username and password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return uhoh("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    # GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/postadvice", methods=["GET", "POST"])
@login_required
def postadvice():
    """Post advice."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("title") or not request.form.get("advice"):
            return uhoh("missing title or advice", 400)

        # Get language id based on what language was selected
        language_id = db.execute("SELECT language_id FROM languages WHERE language_name=:name",
                                 name=request.form.get("language"))[0]["language_id"]

        # Get category id based on what category was selected
        category_id = db.execute("SELECT category_id FROM categories WHERE category_name=:name",
                                 name=request.form.get("category"))[0]["category_id"]

        # Insert post into posts table
        db.execute("""INSERT INTO posts (user_id, category_id, language_id, title, advice)
                   VALUES (:user_id, :category_id, :language_id, :title, :advice)""",
                   user_id=session["user_id"], category_id=category_id, language_id=language_id,
                   title=request.form.get("title"), advice=request.form.get("advice"))

        # Show user what they posted
        return render_template("posted.html", title=request.form.get("title"),
                               language=request.form.get("language"), category=request.form.get("category"),
                               advice=request.form.get("advice"))

    # GET
    else:
        return render_template("postadvice.html")


@app.route("/myposts")
@login_required
def myposts():
    """Display user's posts."""

    # Get all of users posts
    myposts = db.execute("""SELECT title, language_id, category_id, advice, timestamp
                         FROM posts WHERE user_id=:user_id ORDER BY timestamp DESC""",
                         user_id=session["user_id"])
    if not myposts:
        return uhoh("no posts yet", 400)

    # Get information about languages
    language_ids = db.execute("SELECT language_id, language_name FROM languages")

    # Get information about categories
    category_ids = db.execute("SELECT category_id, category_name FROM categories")

    return render_template("myposts.html", myposts=myposts, language_ids=language_ids,
                           category_ids=category_ids)


@app.route("/addevent", methods=["GET", "POST"])
@login_required
def addevent():
    """Add event."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("event_url") or not request.form.get("description"):
            return uhoh("missing event image url or description", 400)

        # Insert event into events table
        db.execute("""INSERT INTO events (user_id, description, event_url)
                   VALUES (:user_id, :description, :event_url)""",
                   user_id=session["user_id"], description=request.form.get("description"),
                   event_url=request.form.get("event_url"))

        # Show user event they added
        return render_template("added.html", description=request.form.get("description"),
                               event_url=request.form.get("event_url"))

    # GET
    else:
        return render_template("addevent.html")


@app.route("/usage")
@login_required
def usage():
    """Display usage statistics."""

    # Count total number of posts
    posts = db.execute("SELECT COUNT(title) FROM posts")[0]["COUNT(title)"]
    if not posts:
        posts = 0

    # Count number of languages with posts
    languages = db.execute("SELECT COUNT(DISTINCT language_id) FROM posts")[
        0]["COUNT(DISTINCT language_id)"]
    if not languages:
        languages = 0

    # Count number of categories with posts
    categories = (db.execute("SELECT COUNT(DISTINCT category_id) FROM posts"))[
        0]["COUNT(DISTINCT category_id)"]
    if not categories:
        categories = 0

    # Count number of PAFs that have posted
    pafs = db.execute("SELECT COUNT(DISTINCT user_id) FROM posts")[0]["COUNT(DISTINCT user_id)"]
    if not pafs:
        pafs = 0

    # Count total number of events
    events = db.execute("SELECT COUNT(event_id) FROM events")[0]["COUNT(event_id)"]
    if not events:
        events = 0

    return render_template("usage.html", posts=posts, languages=languages,
                           categories=categories, pafs=pafs, events=events)


@app.route("/")
def home():
    """Home screen displays events."""

    # Get all events
    events = db.execute(
        "SELECT description, time_added, event_url FROM events ORDER BY time_added DESC")
    if not events:
        return uhoh("no events yet", 400)

    return render_template("home.html", events=events)


@app.route("/categories", methods=["GET", "POST"])
def category():

     # POST
    if request.method == "POST":

        # User would like to see all posts
        if request.form.get("category") == "Allposts":

            # Get all posts from posts table
            categoryposts = db.execute("""SELECT user_id, title, language_id, advice, timestamp FROM posts
                                       ORDER BY timestamp DESC""")
            if not categoryposts:
                return uhoh("no posts yet", 400)

        # Display posts from specific category
        else:

            # Get category_id based on category selected
            category_id = db.execute("SELECT category_id FROM categories WHERE category_name=:name",
                                     name=request.form.get("category"))[0]["category_id"]

            # Get relevant posts from posts table
            categoryposts = db.execute("""SELECT user_id, title, language_id, advice, timestamp FROM posts
                                       WHERE category_id=:category_id ORDER BY timestamp DESC""", category_id=category_id)
            if not categoryposts:
                return uhoh("no posts in this category yet", 400)

        # Get information about languages
        language_ids = db.execute("SELECT language_id, language_name FROM languages")

        # Get nicknames
        nicknames = db.execute("SELECT id, nickname FROM users")

        return render_template("category.html", category=request.form.get("category"),
                               categoryposts=categoryposts, language_ids=language_ids, nicknames=nicknames)
     # GET
    else:
        return render_template("categories.html")


@app.route("/languages", methods=["GET", "POST"])
def language():

     # POST
    if request.method == "POST":

        # Get language_id based language selected
        language_id = db.execute("SELECT language_id FROM languages WHERE language_name=:name",
                                 name=request.form.get("language"))[0]["language_id"]

        # Get relevant posts from posts table
        languageposts = db.execute("""SELECT user_id, title, category_id, advice, timestamp FROM posts
                                   WHERE language_id=:language_id ORDER BY timestamp DESC""",
                                   language_id=language_id)
        if not languageposts:
            return uhoh("no posts in this language yet", 400)

        # Get information about categories
        category_ids = db.execute("SELECT category_id, category_name FROM categories")

        # Get nicknames
        nicknames = db.execute("SELECT id, nickname FROM users")

        return render_template("language.html", language=request.form.get("language"),
                               languageposts=languageposts, category_ids=category_ids, nicknames=nicknames)

     # GET
    else:
        return render_template("languages.html")


@app.route("/pafs", methods=["GET", "POST"])
def paf():

     # POST
    if request.method == "POST":

        # Get user_id based on paf selected
        user_id = db.execute("SELECT id FROM users WHERE nickname=:nickname",
                             nickname=request.form.get("nickname"))[0]["id"]

        # Get relevant posts from posts table
        pafposts = db.execute("""SELECT category_id, title, language_id, advice, timestamp FROM posts
                              WHERE user_id=:user_id ORDER BY timestamp DESC""", user_id=user_id)
        if not pafposts:
            return uhoh("no posts from this user yet", 400)

        # Get information about categories
        category_ids = db.execute("SELECT category_id, category_name FROM categories")

        # Get information about languages
        language_ids = db.execute("SELECT language_id, language_name FROM languages")

        return render_template("paf.html", nickname=request.form.get("nickname"),
                               category_ids=category_ids, language_ids=language_ids,
                               pafposts=pafposts)
     # GET
    else:

        # Get nicknames
        pafs = db.execute("SELECT nickname FROM users ORDER BY nickname")

        return render_template("pafs.html", pafs=pafs)


def errorhandler(e):
    """Handle error"""
    return uhoh(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
