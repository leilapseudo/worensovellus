import sqlite3
from flask import Flask, redirect, render_template, request, session, send_file, abort, make_response
import io
import config
import db
import items
import users
from werkzeug.security import check_password_hash, generate_password_hash
import imghdr
from flask import make_response, abort
from flask import redirect, url_for, flash


app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    total = db.query("SELECT COUNT(*) FROM items")[0][0]
    total_pages = (total + per_page - 1) // per_page

    sql = "SELECT items.id, items.title, items.description, users.username, users.id AS user_id FROM items, users WHERE items.user_id = users.id ORDER BY items.id DESC LIMIT ? OFFSET ?"
    all_items = db.query(sql, [per_page, offset])
    all_comments = items.get_all_comments()

    like_counts = {}
    for item in all_items:
        result = db.query("SELECT COUNT(*) FROM likes WHERE item_id = ?", [item["id"]])
        like_counts[item["id"]] = result[0][0]

    user_likes = set()
    user_reposts = set()
    repost_counts = {row["item_id"]: row["count"] for row in db.query("SELECT item_id, COUNT(*) AS count FROM reposts GROUP BY item_id")}

    if "user_id" in session:
        liked = db.query("SELECT item_id FROM likes WHERE user_id = ?", [session["user_id"]])
        user_likes = {row["item_id"] for row in liked}
        reposted = db.query("SELECT item_id FROM reposts WHERE username = ?", [session["username"]])
        user_reposts = {row["item_id"] for row in reposted}

    return render_template("index.html", items=all_items, comments=all_comments, like_counts=like_counts, user_likes=user_likes, repost_counts=repost_counts, user_reposts=user_reposts, page=page, total_pages=total_pages)

@app.route("/new_item")
def new_item():
    return render_template("new_item.html")


@app.route("/item/<int:item_id>")
def item(item_id):
    result = items.get_item(item_id)
    if not result:
        abort(404)
    item = result
    comments = items.get_comments(item_id)
    return render_template("show_item.html", item=item, comments=comments)


@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    title = request.form["title"]
    description = request.form["description"]
    section = request.form.get("section", "")
    season = request.form.get("season", "")
    if not title or len(title) > 100 or len(description) > 5000:
        abort(403)
    user_id = session["user_id"]
    image = request.files["image"].read()
    items.add_item(title, description, user_id, image, section, season)
    return redirect("/")


@app.route("/edit_item/<int:id>")
def edit_item(id):
    require_login()
    sql = "SELECT id, title, description, user_id FROM items WHERE id = ?"
    result = db.query(sql, [id])
    if not result:
        abort(404)
    item = result[0]
    if item["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_item.html", item=item)

@app.route("/edit_item", methods=["POST"])
def update_item():
    require_login()
    id = request.form["id"]
    title = request.form["title"]
    description = request.form["description"]
    sql = "SELECT id, user_id FROM items WHERE id = ?"
    result = db.query(sql, [id])
    if not result:
        abort(404)
    if result[0]["user_id"] != session["user_id"]:
        abort(403)
    db.execute("UPDATE items SET title = ?, description = ? WHERE id = ?", [title, description, id])
    return redirect("/")


@app.route("/remove_item/<int:id>")
def remove_item(id):
    require_login()
    db.execute("DELETE FROM comments WHERE item_id = ?", [id])
    db.execute("DELETE FROM items WHERE id = ?", [id])
    return redirect("/")

@app.route("/like/<int:item_id>", methods=["POST"])
def like(item_id):
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    existing = db.query(
        "SELECT * FROM likes WHERE user_id=? AND item_id=?",
        [user_id, item_id]
    )
    if existing:
        db.execute("DELETE FROM likes WHERE user_id=? AND item_id=?", [user_id, item_id])
    else:
        db.execute("INSERT INTO likes (user_id, item_id) VALUES (?, ?)", [user_id, item_id])
    return redirect("/")

@app.route("/repost/<int:id>", methods=["POST"])
def repost(id):
    require_login()
    username = session["username"]
    existing = db.query("SELECT id FROM reposts WHERE username = ? AND item_id = ?", [username, id])
    if existing:
        db.execute("DELETE FROM reposts WHERE username = ? AND item_id = ?", [username, id])
    else:
        db.execute("INSERT INTO reposts (username, item_id) VALUES (?, ?)", [username, id])
    return redirect("/")


@app.route("/search")
def search():
    query = request.args.get("query", "")
    section = request.args.get("section", "")
    season = request.args.get("season", "")

    sql = "SELECT items.id, items.title, items.description, users.username, users.id AS user_id FROM items, users WHERE items.user_id = users.id AND (items.title LIKE ? OR items.description LIKE ?)"
    params = [f"%{query}%", f"%{query}%"]

    if section:
        sql += " AND items.section = ?"
        params.append(section)
    if season:
        sql += " AND items.season = ?"
        params.append(season)

    all_items = db.query(sql, params)
    all_comments = items.get_all_comments()

    like_counts = {}
    for item in all_items:
        result = db.query("SELECT COUNT(*) FROM likes WHERE item_id = ?", [item["id"]])
        like_counts[item["id"]] = result[0][0]

    user_likes = set()
    user_reposts = set()
    repost_counts = {row["item_id"]: row["count"] for row in db.query("SELECT item_id, COUNT(*) AS count FROM reposts GROUP BY item_id")}

    if "user_id" in session:
        liked = db.query("SELECT item_id FROM likes WHERE user_id = ?", [session["user_id"]])
        user_likes = {row["item_id"] for row in liked}
        reposted = db.query("SELECT item_id FROM reposts WHERE username = ?", [session["username"]])
        user_reposts = {row["item_id"] for row in reposted}

    return render_template("index.html", items=all_items, comments=all_comments, like_counts=like_counts, user_likes=user_likes, repost_counts=repost_counts, user_reposts=user_reposts, page=1, total_pages=1)


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
        flash("VIRHE: tunnus on jo varattu", "error")
        return redirect(url_for("index"))

    flash("Tunnus luotu!", "success")
    return redirect(url_for("index"))



@app.route("/comment", methods=["POST"])
def comment():
    item_id = request.form["item_id"]
    content = request.form["content"]
    user_id = session["user_id"]

    sql = "INSERT INTO comments (item_id, user_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [item_id, user_id, content])

    return redirect(url_for("index"))


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
            return "Väärä tunnus tai salasana"


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/<username>")
def user_profile(username):
    user = items.get_user_profile(username)
    if not user:
        abort(404)
    user_items = items.get_user_items(user["id"])
    stats = items.get_user_stats(user["id"])
    user_comments = items.get_comments(user["id"])
    return render_template("profile.html", user=user, items=user_items, stats=stats, comments=user_comments)

def get_user_comments(user_id):
    sql = """
        SELECT comments.content,
               comments.created_at,
               items.id AS item_id
        FROM comments, items
        WHERE comments.item_id = items.id
        AND comments.user_id = ?
        ORDER BY comments.id DESC
    """
    return db.query(sql, [user_id])

@app.route("/profile_image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)
    image_type = imghdr.what(None, h=image)
    mime = f"image/{image_type}" if image_type else "application/octet-stream"
    
    response = make_response(image)
    response.headers.set("Content-Type", mime)
    return response


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()
    if request.method == "GET":
        return render_template("add_image.html")
    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.rsplit(".", 1)[-1].lower() in {"jpg", "jpeg", "png", "webp"}:
            return "Väärä tiedostomuoto"
        image = file.read()
        if len(image) > 100 * 1024:
            return "Liian suuri kuva"
        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + session["username"])


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/")