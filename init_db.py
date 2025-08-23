"""
init_db.py - create the SQLite DB and tables
Run once before first run (or app can create automatically).
"""
import sqlite3

DB = "waiting.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER NOT NULL,
        name TEXT,
        status TEXT NOT NULL DEFAULT 'waiting',
        created_at TEXT NOT NULL
    );
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    ''')
    # initialize next_number if not present
    cur.execute("INSERT OR IGNORE INTO meta(key, value) VALUES ('next_number', '1');")
    conn.commit()
    conn.close()
    print("Initialized DB:", DB)

if __name__ == "__main__":
    init_db()
