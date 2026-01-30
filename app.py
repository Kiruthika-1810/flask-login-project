from flask import Flask, render_template, request, redirect, flash
import pymysql
import bcrypt
import traceback

print("APP STARTED")

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE =================

def get_connection():
    try:
        return pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="password",   # EXACT MySQL password
            database="user_auth_db",
            port=3306
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ================= HOME =================

@app.route("/")
def home():
    return redirect("/login")

# ================= SIGNUP =================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            print("FORM:", username, email, password)

            conn = get_connection()

            if conn is None:
                flash("DB connection failed")
                return redirect("/signup")

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email, username))

            if cursor.fetchone():
                flash("User already exists")
                return redirect("/signup")

            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            cursor.execute(
                "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
                (username, email, hashed)
            )

            conn.commit()

            print("INSERT SUCCESS")

            cursor.close()
            conn.close()

            flash("Signup successful")
            return redirect("/login")

        except Exception:
            print("SIGNUP ERROR")
            traceback.print_exc()
            flash("Signup failed")
            return redirect("/signup")

    return render_template("signup.html")

# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        try:
            email = request.form.get("email")
            password = request.form.get("password")

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT password FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user and bcrypt.checkpw(password.encode(), user[0]):
                return "✅ Login Successful"

            else:
                flash("Invalid credentials")

        except Exception:
            print("LOGIN ERROR")
            traceback.print_exc()

    return render_template("login.html")

# ================= RUN =================

print("Starting Flask Server...")

app.run(host="127.0.0.1", port=5000, debug=True)