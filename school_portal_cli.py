from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change in production

# ✅ Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="school_portal"
)
cursor = db.cursor(dictionary=True)

# ===================== AUTH =====================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    secret = request.form["secret"]

    # Determine role
    if secret == "SALVATION123":
        role = "teacher"
    elif secret == "HEADMASTER321":
        role = "headmaster"
    else:
        flash("Invalid role code!")
        return redirect(url_for("home"))

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (username, password, role))
        db.commit()
        flash("Account created! Please log in.")
    except mysql.connector.IntegrityError:
        flash("Username already exists!")

    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        session["username"] = user["username"]
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid username or password")
        return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))
    return render_template("dashboard.html", role=session["role"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ===================== ATTENDANCE =====================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "role" not in session or session["role"] != "teacher":
        return redirect(url_for("home"))

    # Get all students
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    if request.method == "POST":
        for student in students:
            status = request.form.get(f"status_{student['id']}")
            if status:  # Only save if teacher selected
                cursor.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (%s, CURDATE(), %s)",
                    (student["id"], status),
                )
        db.commit()
        return redirect(url_for("dashboard"))

    return render_template("attendance.html", students=students)


# ===================== SCORES =====================
@app.route("/scores", methods=["GET", "POST"])
def scores():
    if "role" not in session or session["role"] != "teacher":
        return redirect(url_for("home"))

    # Get all students
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    if request.method == "POST":
        subject = request.form.get("subject")
        for student in students:
            score = request.form.get(f"score_{student['id']}")
            if score:
                cursor.execute(
                    "INSERT INTO scores (student_id, teacher_id, subject, score, status) VALUES (%s, %s, %s, %s, 'pending')",
                    (student["id"], session["user_id"], subject, score),
                )
        db.commit()
        return redirect(url_for("dashboard"))

    return render_template("scores.html", students=students)


# ===================== APPROVAL =====================
@app.route("/approval", methods=["GET", "POST"])
def approval():
    if "role" not in session or session["role"] != "headmaster":
        return redirect(url_for("home"))

    if request.method == "POST":
        score_id = request.form.get("score_id")
        action = request.form.get("action")

        if action == "approve":
            cursor.execute("UPDATE scores SET status='approved' WHERE id=%s", (score_id,))
        elif action == "reject":
            cursor.execute("UPDATE scores SET status='rejected' WHERE id=%s", (score_id,))
        db.commit()

    cursor.execute("""
        SELECT s.id, st.name AS student_name, u.username AS teacher_name, s.subject, s.score, s.status
        FROM scores s
        JOIN students st ON s.student_id = st.id
        JOIN users u ON s.teacher_id = u.id
        WHERE s.status = 'pending'
    """)
    pending_scores = cursor.fetchall()

    return render_template("approval.html", scores=pending_scores)

# ===================== REPORTS =====================
@app.route("/reports")
def reports():
    # Only headmaster can access
    if "role" not in session or session["role"] != "headmaster":
        return redirect(url_for("home"))

    # Attendance summary
    cursor.execute("""
        SELECT st.name, 
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS presents,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absents
        FROM students st
        LEFT JOIN attendance a ON st.id = a.student_id
        GROUP BY st.name
    """)
    attendance_summary = cursor.fetchall()

    # Scores summary (only approved scores)
    cursor.execute("""
        SELECT st.name, AVG(s.score) AS avg_score
        FROM students st
        LEFT JOIN scores s ON st.id = s.student_id AND s.status='approved'
        GROUP BY st.name
    """)
    scores_summary = cursor.fetchall()

    return render_template("reports.html",
                           attendance=attendance_summary,
                           scores=scores_summary)


if __name__ == "__main__":
    app.run(debug=True)
