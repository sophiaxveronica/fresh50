from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

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

        # Validate form submission
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # Add user to database
        id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                        username=request.form.get("username"),
                        hash=generate_password_hash(request.form.get("password")))
        if not id:
            return apology("username taken")

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

        # Redirect user to home page
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


@app.route("/")
@login_required
def home():
    """Show home screen."""

    # Render portfolio
    return render_template("home.html")


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
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
        return render_template("post.html")

@app.route("/myposts")
@login_required
def myposts():
    """Display user's posts."""

    myposts = db.execute("SELECT title, language_id, category_id, advice, timestamp FROM posts WHERE user_id=:user_id",
                         user_id=session["user_id"])

    return render_template("myposts.html", myposts=myposts)


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    """Show all categories."""

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
                                       WHERE category_id=:category_id""",
                                       category_id=category_id)

            if not categoryposts:
                return apology("no posts in this category yet", 403)

        # Display posts
        return render_template("category.html", category=request.form.get("category"), categoryposts=categoryposts)

    # GET
    else:

        # Render template
        return render_template("categories.html")


    # # POST
    # if request.method == "POST":

    #     # User chose to see posts from every category
    #     if (request.form.get("category") == 'Allposts'):

    #         # Get posts' information from posts table
    #         categoryposts = db.execute("SELECT user_id, title, language_id, advice, timestamp FROM posts")

    #     # User chose to see posts from a specific category
    #     else:

    #         # Get category id based on what category was selected
    #         category_id = db.execute("SELECT category_id FROM categories WHERE category_name=:name",
    #                                  name=request.form.get("category"))[0]["category_id"]


    #         # Get posts' information from posts table
    #         categoryposts = db.execute("""SELECT user_id, title, language_id, advice, timestamp FROM posts
    #                                     WHERE category_id=:category_id""",
    #                                     category_id=category_id)

    #     # Display posts
    #     return render_template("category.html", category=request.form.get("category"), categoryposts=categoryposts)

    # # GET
    # else:

    #     # Render template
    #     return render_template("categories.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
