import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
from flask import send_file
import io
import items
app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    sql = "SELECT id, title, description FROM items"
    all_items = db.query(sql)
    return render_template("index.html", items=all_items)

@app.route("/new_item")
def new_item():
    all_items = items.get_items()
    return render_template("new_item.html")

@app.route("/item/<int:item_id>")
def item(item_id):
    item = items.get_item(item_id)
    return render_template("show_item.html", item=item)

@app.route("/create_item", methods=["POST"])
def create_item():
    title = request.form["title"]
    description = request.form["description"]
    user_id = session["user_id"]
    image = request.files["image"].read()

    items.add_item(title, description, user_id, image)

    return redirect("/")

@app.route("/edit_item/<int:id>")
def edit_item(id):
    if "username" not in session:
        return redirect("/login")
    sql = "SELECT id, title, description FROM items WHERE id = ?"
    result = db.query(sql, [id])
    item = result[0]
    return render_template("edit_item.html", item=item)

@app.route("/remove_item/<int:id>")
def remove_item(id):
    if "username" not in session:
        return redirect("/login")
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [id])
    return redirect("/")

@app.route("/search")
def search():
    query = request.args.get("query", "")
    sql = "SELECT id, title, description FROM items WHERE title LIKE ? OR description LIKE ?"
    all_items = db.query(sql, [f"%{query}%", f"%{query}%"])
    return render_template("index.html", items=all_items)

@app.route("/image/<int:id>")
def image(id):
    sql = "SELECT image FROM items WHERE id = ?"
    result = db.query(sql, [id])
    return send_file(io.BytesIO(result[0][0]), mimetype="image/jpeg")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if not result:
            return "VIRHE: väärä tunnus tai salasana"

        user_id = result[0][0]
        password_hash = result[0][1]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")