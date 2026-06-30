import sqlite3

def login(username, password):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cur.execute(query)
    return cur.fetchone()

ADMIN_PASSWORD = "admin1234!"