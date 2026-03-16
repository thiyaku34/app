from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret"

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Online users dictionary
online_users = {}

# Database helper
def db():
    if not os.path.exists("users.db"):
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        con.commit()
        con.close()
    return sqlite3.connect("users.db")


# ---------------- Routes ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = username
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT username FROM users")
    users = cur.fetchall()
    con.close()
    return render_template("home.html", users=users)

@app.route("/chat/<user>")
def chat(user):
    if "user" not in session:
        return redirect("/")
    return render_template("chat.html", user=user)

@app.route("/admin")
def admin():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    con.close()
    return render_template("admin.html", users=users)

# ---------------- SocketIO Events ---------------- #

@socketio.on("connect")
def connect():
    username = session.get("user")
    if username:
        online_users[username] = request.sid
        emit("status", {"user": username, "status": "online"}, broadcast=True)

@socketio.on("private_message")
def private(data):
    to = data["to"]
    msg = data["msg"]
    if to in online_users:
        emit("message", {"user": session['user'], "msg": msg}, room=online_users[to])

# Image message
@socketio.on("image_message")
def image(data):
    to = data["to"]
    img = data["image"]
    if to in online_users:
        emit("image_message", {"user": session['user'], "image": img}, room=online_users[to])

# ---------------- WebRTC Call Signaling ---------------- #

@socketio.on("call_user")
def call(data):
    to = data["to"]
    if to in online_users:
        emit("incoming_call", {"from": session['user']}, room=online_users[to])

@socketio.on("signal")
def signal(data):
    to = data["to"]
    if to in online_users:
        emit("signal", data, room=online_users[to])

# ---------------- Typing Indicator ---------------- #

@socketio.on("typing")
def typing(data):
    to = data.get("to")
    status = data.get("status")
    if to in online_users:
        emit("typing", {"user": session['user'], "status": status}, room=online_users[to])

# ---------------- Run Server ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)