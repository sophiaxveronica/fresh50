from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

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

    # POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("missing username")

        # Ensure username was submitted
        if not request.form.get("nickname"):
            return apology("missing nickname")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("missing password")

        # Ensure password confirmation was submitted and matches password
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("confirmation either wasn't submitted or doesn't match password")

        # Check if user indicated that they were a paf
        # if request.form.get("paf"):
        #     paf = 1
        # else:
        #     paf = 0 # student

        # Add user to database
        id = db.execute("INSERT INTO users (username, hash, nickname) VALUES(:username, :hash, :nickname)",
                        username=request.form.get("username"),
                        hash=generate_password_hash(request.form.get("password")),
                        nickname=request.form.get("nickname"))
        if not id:
            return apology("username or nickname taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
    """Post."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("title"):
            return apology("missing title")

        # Validate form submission
        if not request.form.get("advice"):
            return apology("missing advice")

        # Get language id based on what language was selected
        language_id = db.execute("SELECT language_id FROM languages WHERE language_name=:name",
                                 name=request.form.get("language"))[0]["language_id"]

        # Get category id based on what category was selected
        category_id = db.execute("SELECT category_id FROM categories WHERE category_name=:name",
                                 name=request.form.get("category"))[0]["category_id"]

        # Insert post information into posts table
        db.execute("""INSERT INTO posts (user_id, category_id, language_id, title, advice)
                   VALUES (:user_id, :category_id, :language_id, :title, :advice)""",
                   user_id=session["user_id"], category_id=category_id,
                   language_id=language_id, title=request.form.get("title"),
                   advice=request.form.get("advice"))

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

    myposts = db.execute("SELECT title, language_id, category_id, advice, timestamp FROM posts WHERE user_id=:user_id",
                         user_id=session["user_id"])

    language_ids = db.execute("SELECT language_id, language_name FROM languages")
    category_ids = db.execute("SELECT category_id, category_name FROM categories")

    return render_template("myposts.html", myposts=myposts, language_ids=language_ids, category_ids=category_ids)


@app.route("/usages")
@login_required
def usages():
    """Display usage statistcis."""

    titles = db.execute("SELECT COUNT(title) FROM posts")[0]["COUNT(title)"]

    languages = db.execute("SELECT COUNT(DISTINCT language_id) FROM posts")[0]["COUNT(DISTINCT language_id)"]

    categories = (db.execute("SELECT COUNT(DISTINCT category_id) FROM posts"))[0]["COUNT(DISTINCT category_id)"]

    pafs = db.execute("SELECT COUNT(username) FROM users")[0]["COUNT(username)"]

    events = db.execute("SELECT COUNT(event_id) FROM events")[0]["COUNT(event_id)"]

    return render_template("usages.html", titles=titles, languages=languages, categories=categories, pafs=pafs, events=events)



@app.route("/addevent", methods=["GET", "POST"])
@login_required
def addevent():
    """Add event."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("event_url"):
            return apology("please event image url")

        # Insert event information into events table
        db.execute("""INSERT INTO events (user_id, description, event_url)
                   VALUES (:user_id, :description, :event_url)""",
                   user_id=session["user_id"], description=request.form.get("description"),
                   event_url=request.form.get("event_url"))

        # Show user what they posted
        return render_template("added.html", description=request.form.get("description"),
                               event_url=request.form.get("event_url"))

    # GET
    else:
        return render_template("addevent.html")


#@app.route("/", methods=["GET", "POST"])
@app.route("/")

def home():
    """Home screen: can pick by category and see events."""

    # # POST
    # if request.method == "POST":

        # # Validate form submission
        # if not request.form.get("category"):
        #     return apology("error")

        # # User chose to see posts from every category
        # if (request.form.get("category") == 'Allposts'):

        #     # Get posts' information from posts table
        #     categoryposts = db.execute("SELECT user_id, title, language_id, advice, timestamp FROM posts")

        # # User chose to see posts from a specific category
        # else:

        #     # Get category id based on what category was selected
        #     category_id = db.execute("SELECT category_id FROM categories WHERE category_name=:name",
        #                              name=request.form.get("category"))[0]["category_id"]

        #     # Get posts' information from posts table
        #     categoryposts = db.execute("""SELECT user_id, title, language_id, advice, timestamp FROM posts
        #                               WHERE category_id=:category_id""", category_id=category_id)

        #     if not categoryposts:
        #         return apology("no posts in this category yet", 403)

        # language_ids = db.execute("SELECT language_id, language_name FROM languages")
        # nicknames = db.execute("SELECT id, nickname FROM users")

        # # Display posts
        # return render_template("category.html", category=request.form.get("category"),
        #                       categoryposts=categoryposts, language_ids=language_ids, nicknames=nicknames)

    # # GET
    # else:

    events = db.execute("SELECT description, time_added, event_url FROM events ORDER BY time_added DESC")
#     # Render template
        return render_template("home.html", events=events)


@app.route("/categories", methods=["GET", "POST"])
def category():

     # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("category"):
            return apology("error")

        # User chose to see posts from every category
        if (request.form.get("category") == 'Allposts'):

            # Get posts' information from posts table
            categoryposts = db.execute("SELECT user_id, title, language_id, advice, timestamp FROM posts")

        # User chose to see posts from a specific category
        else:

            # Get category id based on what category was selected
            category_id = db.execute("SELECT category_id FROM categories WHERE category_name=:name",
                                     name=request.form.get("category"))[0]["category_id"]

            # Get posts' information from posts table
            categoryposts = db.execute("""SELECT user_id, title, language_id, advice, timestamp FROM posts
                                       WHERE category_id=:category_id""", category_id=category_id)

            if not categoryposts:
                return apology("no posts in this category yet", 403)

        language_ids = db.execute("SELECT language_id, language_name FROM languages")
        nicknames = db.execute("SELECT id, nickname FROM users")

        # Display posts
        return render_template("category.html", category=request.form.get("category"),
                               categoryposts=categoryposts, language_ids=language_ids, nicknames=nicknames)
     # GET
    else:

        # Render template
        return render_template("categories.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
