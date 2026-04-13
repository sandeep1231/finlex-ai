import sqlite3
conn = sqlite3.connect('finlex.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in cursor.fetchall():
    print(t[0])
conn.close()
