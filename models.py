"""
models.py - lightweight SQLite helpers for the Waiting Line System
"""

import sqlite3
from datetime import datetime

DB = "waiting.db"

def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_missing():
    # Ensure DB initialized if file exists but tables missing
    conn = get_conn()
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
    cur.execute("INSERT OR IGNORE INTO meta(key, value) VALUES ('next_number', '1');")
    conn.commit()
    conn.close()

def get_next_number():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM meta WHERE key='next_number'")
    row = cur.fetchone()
    if row is None:
        # fallback, initialize
        cur.execute("INSERT OR REPLACE INTO meta(key,value) VALUES ('next_number','1')")
        conn.commit()
        n = 1
    else:
        n = int(row['value'])
    # increment counter
    cur.execute("UPDATE meta SET value=? WHERE key='next_number'", (str(n+1),))
    conn.commit()
    conn.close()
    return n

def create_ticket(name=None):
    num = get_next_number()
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO tickets (number, name, status, created_at) VALUES (?, ?, 'waiting', ?)",
                (num, name, now))
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return {'id': tid, 'number': num, 'name': name, 'status': 'waiting', 'created_at': now}

def list_tickets(status=None):
    conn = get_conn()
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM tickets WHERE status=? ORDER BY id ASC", (status,))
    else:
        cur.execute("SELECT * FROM tickets ORDER BY id ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def serve_next():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets WHERE status='waiting' ORDER BY id ASC LIMIT 1")
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute("UPDATE tickets SET status='served' WHERE id=?", (row['id'],))
    conn.commit()
    served = dict(row)
    served['status'] = 'served'
    conn.close()
    return served

def update_status(ticket_id, status):
    if status not in ('waiting', 'served', 'cancelled'):
        raise ValueError("invalid status")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()
    return True
