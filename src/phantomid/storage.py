import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                password_hash TEXT,
                consent INTEGER NOT NULL DEFAULT 0,
                consent_version INTEGER,
                consent_at TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                type TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id),
                payload BLOB NOT NULL
            );
        """)
        # Earlier prototype databases contain only username and role.
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(users)")}
        for name, definition in {
            "password_hash": "TEXT",
            "consent": "INTEGER NOT NULL DEFAULT 0",
            "consent_version": "INTEGER",
            "consent_at": "TEXT",
        }.items():
            if name not in columns:
                self.conn.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")
        self.conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS users_name ON users(username COLLATE NOCASE)"
        )
        self.conn.commit()

    def add_user(self, username, role="user", password_hash=None):
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO users(username, role, password_hash) VALUES (?, ?, ?)",
                (username, role, password_hash),
            )
        return cursor.lastrowid

    def find_user(self, username):
        return self.conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)
        ).fetchone()

    def users(self):
        return self.conn.execute(
            "SELECT id, username, role, consent FROM users ORDER BY id"
        ).fetchall()

    def set_consent(self, user_id, accepted):
        with self.conn:
            self.conn.execute(
                "UPDATE users SET consent=?, consent_version=1, consent_at=datetime('now') WHERE id=?",
                (int(accepted), user_id),
            )

    def add_event(self, user_id, event_type):
        if event_type not in {
            "consent_accepted",
            "consent_withdrawn",
            "challenge_demo",
            "verified_demo",
            "challenge_detected",
            "verified",
        }:
            raise ValueError("Unsupported event type")
        with self.conn:
            self.conn.execute(
                "INSERT INTO events(user_id, type) VALUES (?, ?)", (user_id, event_type)
            )
            self.conn.execute(
                "DELETE FROM events WHERE created_at < datetime('now', '-30 days')"
            )

    def events(self, user_id):
        return self.conn.execute(
            "SELECT type, created_at FROM events WHERE user_id=? AND created_at >= datetime('now', '-30 days') ORDER BY id DESC LIMIT 50",
            (user_id,),
        ).fetchall()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
