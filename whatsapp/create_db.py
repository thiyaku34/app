import sqlite3

# database create
conn = sqlite3.connect("users.db")

cursor = conn.cursor()

# table create
cursor.execute("""
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# sample users insert
cursor.execute("INSERT INTO users (username,password) VALUES ('admin','admin')")
cursor.execute("INSERT INTO users (username,password) VALUES ('user1','123')")
cursor.execute("INSERT INTO users (username,password) VALUES ('user2','123')")

conn.commit()

print("Database created successfully")