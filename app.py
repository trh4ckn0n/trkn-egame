from flask import Flask, render_template, redirect, request
import random
import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "trhacknon_secret"

# Génération d'une plage horaire pour l'événement
def generate_random_time():
    now = datetime.datetime.now()
    start_hour = random.randint(0, 22)  # Entre 00h et 22h (pour laisser de la place aux 10 min)
    start_time = datetime.datetime(now.year, now.month, now.day, start_hour, random.randint(0, 59))
    return start_time, start_time + datetime.timedelta(minutes=10)

# Initialisation des variables globales
WIN_START, WIN_END = generate_random_time()
PASSWORD = ""

# Connexion à SQLite pour stocker les gagnants
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
        PASSWORD = str(random.randint(100000, 999999))  # Génère un mot de passe unique
        conn = sqlite3.connect("winners.db")
        c = conn.cursor()
        c.execute("INSERT INTO winners (password, used) VALUES (?, ?)", (PASSWORD, 0))
        conn.commit()
        conn.close()
        return redirect(f"/win?password={PASSWORD}")
    
    # Calcul de la fourchette d'une heure avant la fenêtre de gain
    next_window = WIN_START.strftime("%Hh")
    next_window_range = f"{int(next_window)}h - {int(next_window)+1}h"

    return render_template("index.html", time_range=next_window_range)

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
