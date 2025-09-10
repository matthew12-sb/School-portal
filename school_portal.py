import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://neondb_owner:npg_e9iVbyEmR4qx@ep-young-bird-ad7ggi1t-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

def get_db():
    return psycopg2.connect(DATABASE_URL)

# -------------------- ROUTES -------------------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/students")
def students():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, class FROM students ORDER BY name;")
    rows = cur.fetchall()
    conn.close()
    return render_template("students.html", students=rows)

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form["name"]
    student_class = request.form["class"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, class) VALUES (%s, %s);", (name, student_class))
    conn.commit()
    conn.close()
    return redirect(url_for("students"))

@app.route("/attendance")
def attendance():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, s.name, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC;
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template("attendance.html", records=rows)

@app.route("/add_attendance", methods=["POST"])
def add_attendance():
    student_id = request.form["student_id"]
    status = request.form["status"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO attendance (student_id, date, status) VALUES (%s, CURRENT_DATE, %s);",
                (student_id, status))
    conn.commit()
    conn.close()
    return redirect(url_for("attendance"))

@app.route("/scores")
def scores():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT sc.id, s.name, sc.subject, sc.score, sc.approved
        FROM scores sc
        JOIN students s ON sc.student_id = s.id
        ORDER BY s.name;
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template("scores.html", scores=rows)

@app.route("/add_score", methods=["POST"])
def add_score():
    student_id = request.form["student_id"]
    subject = request.form["subject"]
    score = request.form["score"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO scores (student_id, subject, score, approved) VALUES (%s, %s, %s, FALSE);",
                (student_id, subject, score))
    conn.commit()
    conn.close()
    return redirect(url_for("scores"))

@app.route("/approve_score/<int:score_id>")
def approve_score(score_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE scores SET approved = TRUE WHERE id = %s;", (score_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("scores"))

# -------------------- RUN -------------------- #
if __name__ == "__main__":
    app.run(debug=True)
