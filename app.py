from flask import Flask, render_template, redirect, request, session
import random
import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "trhacknon_secret"

# Définir une heure aléatoire pour la fenêtre de gain
def generate_random_time():
    now = datetime.datetime.now()
    start_minute = random.randint(0, 23 * 60)  # Entre 00:00 et 23:59
    start_time = datetime.datetime(now.year, now.month, now.day, start_minute // 60, start_minute % 60)
    return start_time, start_time + datetime.timedelta(minutes=10)

# Stocke l'heure de la fenêtre et le mot de passe du jour
WIN_START, WIN_END = generate_random_time()
PASSWORD = ""

# Connexion à la base de données SQLite
def init_db():
    conn = sqlite3.connect("winners.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS winners (id INTEGER PRIMARY KEY, password TEXT, used INTEGER)''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    now = datetime.datetime.now()
    if WIN_START <= now <= WIN_END:
        global PASSWORD
        PASSWORD = str(random.randint(100000, 999999))  # Génère un mot de passe à usage unique
        conn = sqlite3.connect("winners.db")
        c = conn.cursor()
        c.execute("INSERT INTO winners (password, used) VALUES (?, ?)", (PASSWORD, 0))
        conn.commit()
        conn.close()
        return redirect(f"/win?password={PASSWORD}")
    return render_template("index.html", time_left=(WIN_START - now).total_seconds())

@app.route("/win", methods=["GET", "POST"])
def win():
    password = request.args.get("password")
    if password:
        conn = sqlite3.connect("winners.db")
        c = conn.cursor()
        c.execute("SELECT * FROM winners WHERE password=? AND used=0", (password,))
        entry = c.fetchone()
        if entry:
            c.execute("UPDATE winners SET used=1 WHERE password=?", (password,))
            conn.commit()
            conn.close()
            return render_template("win.html", password=password)
        conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0")
