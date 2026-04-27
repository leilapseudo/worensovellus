
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
    image BLOB
    ALTER TABLE users ADD COLUMN image BLOB;
    join_date TEXT DEFAULT (DATE('now'));
);


CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    user_id INTEGER,
    image BLOB
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reposts (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    item_id INTEGER NOT NULL
);