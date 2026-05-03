CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB,
    join_date TEXT DEFAULT (DATE('now'))
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    user_id INTEGER REFERENCES users(id),
    image BLOB,
    section TEXT,
    season TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reposts (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    item_id INTEGER NOT NULL REFERENCES items(id)
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    item_id INTEGER NOT NULL REFERENCES items(id)
);