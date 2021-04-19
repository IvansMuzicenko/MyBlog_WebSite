import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import string
from string import Template

from helpers import login_required, apology, admin_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/debug")
def debug():
    return render_template("debug.html", debug = session.get("user_id"))

@app.route("/")
def index():

    posts = db.execute("SELECT * FROM posts WHERE poststatus = '1' ORDER BY date DESC")

    return render_template("index.html", username=session.get("username"), posts=posts)


@app.route("/post/<post_id>", methods=["GET", "POST"])
def post_page(post_id):

    if request.method == "POST":
        db.execute("INSERT INTO comments (post_id, username, content, date) VALUES (:post_id, :username, :content, CURRENT_TIMESTAMP)",
        post_id = post_id,
        username = session.get("username"),
        content = request.form.get("comment"))

        return redirect(f"/post/{post_id}")

    else:
        post = db.execute("SELECT * FROM posts WHERE id = :postid AND poststatus = '1' ", postid = post_id)
        if not post:
            return apology("post not found", 404)

        comments = db.execute("SELECT * FROM comments WHERE post_id = :postid", postid = post_id)

        return render_template("post.html", post=post[0], comments=comments, username=session.get("username"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")


        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["status"] = rows[0]["status"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return ("Must provide username")
            return redirect("/register")

        elif len(request.form.get("username")) < 6:
            flash("Username must contain at least 6 symbols")
            return redirect("/register")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/register")

        elif len(request.form.get("password")) < 6:
            flash("Password must contain at least 6 symbols")
            return redirect("/register")

        elif not request.form.get("confirmation"):
            flash("Must provide password confirmation")
            return redirect("/register")

        elif not (request.form.get("password") == request.form.get("confirmation")):
            flash("Passwords don't match")
            return redirect("/register")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) >= 1 :
            flash("username is already taken")
            return redirect("/register")

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES(:username, :password)", username=username, password=password)

        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/profile")
@login_required
def profile():

    rows = db.execute("SELECT c.content, p.title, c.date FROM comments AS c JOIN posts AS p ON c.post_id = p.id WHERE c.username = :username ORDER BY c.date DESC;", username = session.get("username"))

    return render_template("profile.html", comments = rows, username=session.get("username"))


@app.route("/addpost", methods=["GET", "POST"])
@login_required
@admin_required
def addpost():
    if request.method == "POST":
        description = request.form.get("content")[0:len(request.form.get("content"))//2]
        db.execute("INSERT INTO posts (title, content, description, date) VALUES (:title, :content, :description, CURRENT_TIMESTAMP)",
        title = request.form.get("title"),
        content = request.form.get("content"),
        description = description)
        return redirect("/")

    else:
        return render_template("addpost.html", username=session.get("username"))


@app.route("/contacts")
@login_required
def contacts():
    return render_template("contacts.html", username=session.get("username"))

@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "POST":
        if not request.form.get("oldpassword"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        elif not (request.form.get("newpassword") == request.form.get("confirmation")):
            return apology("passwords don't match", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=session["username"])

        if not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            return apology("invalid password", 403)

        password = generate_password_hash(request.form.get("newpassword"))

        db.execute("UPDATE users SET hash = :password WHERE id = :user", password=password, user=session["user_id"])

        return redirect("/profile")
    else:
        return render_template("changepass.html", username=session.get("username"))

@app.route("/comments")
@login_required
def comments():


    rows = db.execute("SELECT c.content, p.title, c.date FROM comments AS c JOIN posts AS p ON c.post_id = p.id WHERE c.username = :username ORDER BY c.date DESC;", username = session.get("username"))

    return render_template("comments.html", comments = rows, username=session.get("username"))

@app.route("/aboutme")
@login_required
def aboutme():
    return render_template("aboutme.html", username=session.get("username"))

@app.route("/adminpanel", methods=["GET", "POST"])
@login_required
@admin_required
def adminpanel():
        posts = db.execute("SELECT * FROM posts WHERE poststatus = '1' ORDER BY date DESC")
        del_posts = db.execute("SELECT * FROM posts WHERE poststatus = '0' ORDER BY date DESC")

        return render_template("adminpanel.html", username=session.get("username"), posts = posts, del_posts = del_posts)

@app.route("/deleteall")
@login_required
@admin_required
def deleteall():
    db.execute("UPDATE posts SET poststatus = '0'")
    return redirect("/adminpanel")

@app.route("/recoverall")
@login_required
@admin_required
def recoverall():
    db.execute("UPDATE posts SET poststatus = '1'")
    return redirect("/adminpanel")

@app.route("/fulldeleteall")
@login_required
@admin_required
def fulldeleteall():
    db.execute("DELETE FROM posts WHERE poststatus = '0'")
    return redirect("/adminpanel")

@app.route("/edit<post_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_post(post_id):

    if request.method == "POST":
        db.execute("UPDATE posts SET title = :title, content = :content WHERE id = :post_id",
        post_id = post_id,
        title = request.form.get("edittitle"),
        content = request.form.get("editcontent"))

        return redirect(f"/post/{post_id}")

    else:
        post = db.execute("SELECT * FROM posts WHERE id = :postid", postid = post_id)
        if not post:
            return apology("post not found", 404)

        return render_template("editpost.html", post=post[0], username=session.get("username"))

@app.route("/delete<post_id>")
@login_required
@admin_required
def delete(post_id):
    db.execute("UPDATE posts SET poststatus = '0' WHERE id = :post_id", post_id = post_id)

    return redirect("/adminpanel")

@app.route("/recover<post_id>")
@login_required
@admin_required
def recover(post_id):
    db.execute("UPDATE posts SET poststatus = '1' WHERE id = :post_id", post_id = post_id)

    return redirect("/adminpanel")

@app.route("/fulldelete<post_id>")
@login_required
@admin_required
def fulldelete(post_id):
    db.execute("DELETE FROM posts WHERE poststatus = '0' AND id = :post_id", post_id = post_id)

    return redirect("/adminpanel")




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
