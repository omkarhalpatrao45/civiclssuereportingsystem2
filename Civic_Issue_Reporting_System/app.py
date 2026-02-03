from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------------- CONFIG ----------------

app = Flask(__name__)
CORS(app)

# Secret key from Render Environment Variables
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE = os.path.join(BASE_DIR, "database.db")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            photo_path TEXT,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print("DB INIT ERROR:", e)

# ---------------- HELPERS ----------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

# ---------- USER AUTH ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password),
            )
            conn.commit()
            flash("Registration successful", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists", "error")
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "error")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    issues = conn.execute(
        "SELECT * FROM issues WHERE user_id=?",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template("dashboard.html", issues=issues)

# ---------- ADMIN LOGIN ----------

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute(
            "SELECT * FROM users WHERE email=? AND role='admin'",
            (email,),
        ).fetchone()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin_id"] = admin["user_id"]
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials", "error")

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    issues = conn.execute("SELECT * FROM issues").fetchall()
    conn.close()

    return render_template("admin_dashboard.html", issues=issues)

# ---------- ISSUE REPORT ----------

@app.route("/report", methods=["GET", "POST"])
def report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]

        photo = request.files.get("photo")
        photo_path = None

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            photo.save(photo_path)

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO issues (title, description, photo_path, location, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, description, photo_path, location, session["user_id"]),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("report.html")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run()

