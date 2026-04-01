import db

def add_item(title, description, user_id, image):
    sql = "INSERT INTO items (title, description, user_id, image) VALUES (?, ?, ?, ?)"
    db.execute(sql, [title, description, user_id, image])


def get_items():
    sql = "SELECT id, title FROM items ORDER BY id DESC"
    return db.query(sql)


def get_item(item_id):
    sql = """SELECT items.title, items.description, items.image, users.username
             FROM items, users
             WHERE items.user_id = users.id AND items.id = ?"""
    return db.query(sql, [item_id])