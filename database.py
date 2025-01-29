import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  date TEXT NOT NULL,
                  sleep_hours REAL,
                  sleep_quality TEXT,
                  mood TEXT,
                  meals TEXT,
                  activities TEXT,
                  notes TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()


def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, generate_password_hash(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return check_password_hash(result[0], password)
    return False


def add_daily_log(username, date, sleep_hours, sleep_quality, mood, meals, activities, notes):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()[0]

        c.execute("""INSERT INTO daily_logs 
                    (user_id, date, sleep_hours, sleep_quality, mood, meals, activities, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (user_id, date, sleep_hours, sleep_quality, mood, json.dumps(meals), json.dumps(activities), notes))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding daily log: {e}")
        return False
    finally:
        conn.close()


def get_daily_logs(username, start_date, end_date):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()[0]

        c.execute("""SELECT date, sleep_hours, sleep_quality, mood, meals, activities, notes 
                    FROM daily_logs 
                    WHERE user_id = ? AND date BETWEEN ? AND ?
                    ORDER BY date DESC""", (user_id, start_date, end_date))

        logs = c.fetchall()
        return [
            {
                "date": log[0],
                "sleep_hours": log[1],
                "sleep_quality": log[2],
                "mood": log[3],
                "meals": json.loads(log[4]),
                "activities": json.loads(log[5]),
                "notes": log[6]
            }
            for log in logs
        ]
    finally:
        conn.close()


def get_date_range(username, range_type):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()[0]

        c.execute("SELECT MIN(date), MAX(date) FROM daily_logs WHERE user_id = ?", (user_id,))
        min_date, max_date = c.fetchone()

        if not min_date or not max_date:
            return None, None

        min_date = datetime.strptime(min_date, '%Y-%m-%d')
        max_date = datetime.strptime(max_date, '%Y-%m-%d')

        if range_type == 'week':
            start_date = max_date - timedelta(days=7)
        elif range_type == 'month':
            start_date = max_date - timedelta(days=30)
        elif range_type == 'year':
            start_date = max_date - timedelta(days=365)
        else:
            start_date = min_date

        return start_date.strftime('%Y-%m-%d'), max_date.strftime('%Y-%m-%d')
    finally:
        conn.close()