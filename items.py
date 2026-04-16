import db

def add_item(title, description, user_id, image, section, season):
    sql = "INSERT INTO items (title, description, user_id, image, section, season) VALUES (?, ?, ?, ?, ?, ?)"
    db.execute(sql, [title, description, user_id, image, section, season])


def get_items():
    sql = "SELECT id, title FROM items ORDER BY id DESC"
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.id, items.title, items.description, items.image, users.username
             FROM items, users
             WHERE items.user_id = users.id AND items.id = ?"""
    result = db.query(sql, [item_id])
    return result[0] if result else None

def get_user_profile(username):
    sql = "SELECT id, username, join_date FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None

def get_user_items(user_id):
    sql = "SELECT id, title, description FROM items WHERE user_id = ? ORDER BY id DESC"
    return db.query(sql, [user_id])

def get_user_stats(user_id):
    post_count = db.query("SELECT COUNT(*) as count FROM items WHERE user_id = ?", [user_id])[0]["count"]
    comment_count = db.query("SELECT COUNT(*) as count FROM comments WHERE user_id = ?", [user_id])[0]["count"]
    return {"post_count": post_count}

def add_comment(item_id, user_id, content):
    sql = "INSERT INTO comments (item_id, user_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [item_id, user_id, content])

def get_comments(item_id):
    sql = """SELECT comments.content, comments.created_at, users.username
             FROM comments, users
             WHERE comments.user_id = users.id AND comments.item_id = ?
             ORDER BY comments.id ASC"""
    return db.query(sql, [item_id])

def get_all_comments():
    sql = """
        SELECT comments.content,
               comments.item_id,
               users.username
        FROM comments, users
        WHERE comments.user_id = users.id
        ORDER BY comments.id DESC
    """
    return db.query(sql)