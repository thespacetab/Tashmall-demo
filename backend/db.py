import sqlite3

conn = sqlite3.connect('tashmall.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM users')  # или shops, если аккаунты в этой таблице
for row in cursor.fetchall():
    print(row)
conn.close()