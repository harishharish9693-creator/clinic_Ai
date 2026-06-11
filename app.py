from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import sqlite3
from datetime import datetime
import google.generativeai as genai
import os
import typing as t
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
try:
    import pymysql
    from pymysql.cursors import DictCursor
except Exception:
    pymysql = None
    DictCursor = None

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-me')

# Set up Google GenAI with environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize model correctly
model = genai.GenerativeModel("gen-lang-client-0021793478")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

 

@app.route('/books')
def books():
    return render_template('books.html')

@app.route('/doc_appointment')
def doc_appointment():
    return render_template('doc_appointment.html')

@app.route('/dementia')
def dementia():
    return render_template('dementia.html')

@app.route('/caregiver')
def caregiver():
    return render_template('caregiver.html')

@app.route('/music')
def music():
    return render_template('music.html')

@app.route('/panic')
def panic():
    return render_template('panic.html')

@app.route('/games')
def games():
    return render_template('games.html')


@app.route('/max_ai')
def max_ai():
    return render_template('max_ai.html')

@app.route('/language')
def language():
    return render_template('language.html')

@app.route("/api/ask_max", methods=["POST"])
def ask_max():
    data = request.get_json()
    query = data.get("query", "")
    response = model.generate_content(f"You are a helpful assistant for dementia patients. Respond kindly and simply: {query}")
    return jsonify({"reply": response.text})

# ---------------------- Appointment Database Setup ----------------------

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'appointments.db')
if os.environ.get('VERCEL') == '1':
    # Vercel has a read-only filesystem except for /tmp
    VERCEL_DB_PATH = '/tmp/appointments.db'
    if not os.path.exists(VERCEL_DB_PATH) and os.path.exists(DATABASE_PATH):
        import shutil
        try:
            shutil.copy(DATABASE_PATH, VERCEL_DB_PATH)
        except Exception as e:
            print(f"Error copying database to /tmp: {e}")
    DATABASE_PATH = VERCEL_DB_PATH

USE_MYSQL = bool(os.getenv('MYSQL_HOST'))


def get_db_connection():
    if USE_MYSQL:
        if pymysql is None:
            raise RuntimeError('pymysql not installed. Please install with: pip install pymysql')
        host = os.getenv('MYSQL_HOST', '127.0.0.1')
        port = int(os.getenv('MYSQL_PORT', '3306'))
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        database = os.getenv('MYSQL_DATABASE', 'appointments_db')
        return pymysql.connect(host=host, port=port, user=user, password=password, database=database, cursorclass=DictCursor, autocommit=False)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            conn.cursor().execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    `date` DATE NOT NULL,
                    doctor VARCHAR(255) NOT NULL,
                    message TEXT,
                    created_at DATETIME NOT NULL,
                    assigned_doctor VARCHAR(255) NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending'
                )
                """
            )
            # Family contacts table
            conn.cursor().execute(
                """
                CREATE TABLE IF NOT EXISTS family_contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(100) NOT NULL
                )
                """
            )
            # Ensure new columns exist in case table was created earlier without them
            cur = conn.cursor()
            try:
                cur.execute("ALTER TABLE appointments ADD COLUMN assigned_doctor VARCHAR(255) NULL")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE appointments ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'pending'")
            except Exception:
                pass
            # Users table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL
                )
                """
            )
        else:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    department TEXT NOT NULL,
                    date TEXT NOT NULL,
                    doctor TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    assigned_doctor TEXT,
                    status TEXT NOT NULL DEFAULT 'pending'
                )
                """
            )
            # Family contacts table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS family_contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL
                )
                """
            )
            # Add columns for existing DBs if missing
            try:
                conn.execute("ALTER TABLE appointments ADD COLUMN assigned_doctor TEXT")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE appointments ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")
            except Exception:
                pass
            # Users table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                )
                """
            )
        conn.commit()
    finally:
        conn.close()


def create_default_admin_if_needed():
    username = os.getenv('ADMIN_USERNAME')
    password = os.getenv('ADMIN_PASSWORD')
    if not username or not password:
        return
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            cur.execute('SELECT id FROM users WHERE username=%s', (username,))
            row = cur.fetchone()
            if not row:
                cur.execute('INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                            (username, None, generate_password_hash(password), 'admin'))
        else:
            row = conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
            if not row:
                conn.execute('INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                             (username, None, generate_password_hash(password), 'admin'))
        conn.commit()
    finally:
        conn.close()


def login_required(role: t.Optional[str] = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login', next=request.path))
            if role and session.get('role') != role:
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/appointment', methods=['GET', 'POST'])
@login_required(role='patient')
def appointment_page():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        date = request.form.get('date', '').strip()
        doctor = request.form.get('doctor', '').strip()
        message = request.form.get('message', '').strip()

        if not (name and email and phone and department and date and doctor):
            return render_template('appointment.html', error_message='All required fields must be filled.'), 400

        conn = get_db_connection()
        try:
            if USE_MYSQL:
                conn.cursor().execute(
                    'INSERT INTO appointments (name, email, phone, department, `date`, doctor, message, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (name, email, phone, department, date, doctor, message, datetime.utcnow())
                )
            else:
                conn.execute(
                    'INSERT INTO appointments (name, email, phone, department, date, doctor, message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (name, email, phone, department, date, doctor, message, datetime.utcnow().isoformat())
                )
            conn.commit()
        finally:
            conn.close()

        return render_template('appointment.html', success_message='Your appointment has been saved. We will contact you shortly!')

    return render_template('appointment.html')

@app.route('/api/appointments', methods=['GET'])
def list_appointments():
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            cur.execute('SELECT id, name, email, phone, department, `date`, doctor, message, created_at, assigned_doctor, status FROM appointments ORDER BY id DESC')
            rows = cur.fetchall()
        else:
            rows = conn.execute('SELECT id, name, email, phone, department, date, doctor, message, created_at, assigned_doctor, status FROM appointments ORDER BY id DESC').fetchall()
        data = [dict(row) for row in rows]
        return jsonify(data)
    finally:
        conn.close()

# ---------------------- Admin Views ----------------------

@app.route('/admin/appointments', methods=['GET'])
@login_required(role='admin')
def admin_appointments():
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            cur.execute('SELECT id, name, email, phone, department, `date`, doctor, message, created_at, assigned_doctor, status FROM appointments ORDER BY id DESC')
            rows = cur.fetchall()
        else:
            rows = conn.execute('SELECT id, name, email, phone, department, date, doctor, message, created_at, assigned_doctor, status FROM appointments ORDER BY id DESC').fetchall()
        appointments = [dict(row) for row in rows]
        return render_template('admin_appointments.html', appointments=appointments)
    finally:
        conn.close()

@app.route('/admin/assign', methods=['POST'])
@login_required(role='admin')
def admin_assign():
    appointment_id = request.form.get('appointment_id')
    assigned_doctor = request.form.get('assigned_doctor', '').strip()
    status = request.form.get('status', 'assigned').strip()
    if not appointment_id or not assigned_doctor:
        return redirect(url_for('admin_appointments'))
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            cur.execute('UPDATE appointments SET assigned_doctor=%s, status=%s WHERE id=%s', (assigned_doctor, status, appointment_id))
        else:
            conn.execute('UPDATE appointments SET assigned_doctor=?, status=? WHERE id=?', (assigned_doctor, status, appointment_id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('admin_appointments'))


# ---------------------- Auth ----------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'patient').strip()
        if role not in ('patient', 'doctor'):
            role = 'patient'
        if not username or not password:
            return render_template('register.html', error_message='Username and password are required.')
        conn = get_db_connection()
        try:
            if USE_MYSQL:
                cur = conn.cursor()
                cur.execute('SELECT id FROM users WHERE username=%s', (username,))
                if cur.fetchone():
                    return render_template('register.html', error_message='Username already exists.')
                cur.execute('INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                            (username, email or None, generate_password_hash(password), role))
            else:
                row = conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
                if row:
                    return render_template('register.html', error_message='Username already exists.')
                conn.execute('INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                             (username, email or None, generate_password_hash(password), role))
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db_connection()
        try:
            if USE_MYSQL:
                cur = conn.cursor()
                cur.execute('SELECT id, username, email, password_hash, role FROM users WHERE username=%s', (username,))
                user = cur.fetchone()
            else:
                user = conn.execute('SELECT id, username, email, password_hash, role FROM users WHERE username=?', (username,)).fetchone()
        finally:
            conn.close()
        if not user or not check_password_hash(user['password_hash'], password):
            return render_template('login.html', error_message='Invalid username or password.')
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user.get('email') if isinstance(user, dict) else user['email']
        session['role'] = user['role']
        next_url = request.args.get('next')
        if next_url:
            return redirect(next_url)
        if user['role'] == 'admin':
            return redirect(url_for('admin_appointments'))
        if user['role'] == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------- Dashboards ----------------------

@app.route('/doctor/dashboard')
@login_required(role='doctor')
def doctor_dashboard():
    username = session.get('username')
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            cur.execute('SELECT * FROM appointments WHERE assigned_doctor=%s ORDER BY id DESC', (username,))
            rows = cur.fetchall()
        else:
            rows = conn.execute('SELECT * FROM appointments WHERE assigned_doctor=? ORDER BY id DESC', (username,)).fetchall()
        appointments = [dict(row) for row in rows]
    finally:
        conn.close()
    return render_template('doctor_dashboard.html', appointments=appointments)


@app.route('/patient/dashboard')
@login_required(role='patient')
def patient_dashboard():
    email = session.get('email')
    username = session.get('username')
    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            # Match by email if available, else by name
            if email:
                cur.execute('SELECT * FROM appointments WHERE email=%s ORDER BY id DESC', (email,))
            else:
                cur.execute('SELECT * FROM appointments WHERE name=%s ORDER BY id DESC', (username,))
            rows = cur.fetchall()
        else:
            if email:
                rows = conn.execute('SELECT * FROM appointments WHERE email=? ORDER BY id DESC', (email,)).fetchall()
            else:
                rows = conn.execute('SELECT * FROM appointments WHERE name=? ORDER BY id DESC', (username,)).fetchall()
        appointments = [dict(row) for row in rows]
    finally:
        conn.close()
    return render_template('patient_dashboard.html', appointments=appointments)


@app.route('/family', methods=['GET', 'POST'])
@login_required(role='patient')
def family():
    user_id = session.get('user_id')
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        if name and phone:
            conn = get_db_connection()
            try:
                if USE_MYSQL:
                    conn.cursor().execute('INSERT INTO family_contacts (user_id, name, phone) VALUES (%s, %s, %s)', (user_id, name, phone))
                else:
                    conn.execute('INSERT INTO family_contacts (user_id, name, phone) VALUES (?, ?, ?)', (user_id, name, phone))
                conn.commit()
            finally:
                conn.close()
        return redirect(url_for('family'))

    conn = get_db_connection()
    try:
        if USE_MYSQL:
            cur = conn.cursor()
            cur.execute('SELECT id, name, phone FROM family_contacts WHERE user_id=%s ORDER BY id DESC', (user_id,))
            rows = cur.fetchall()
            contacts = [dict(row) for row in rows]
        else:
            rows = conn.execute('SELECT id, name, phone FROM family_contacts WHERE user_id=? ORDER BY id DESC', (user_id,)).fetchall()
            contacts = [dict(row) for row in rows]
    finally:
        conn.close()
    return render_template('family.html', contacts=contacts)
# Initialize database on startup
init_db()
create_default_admin_if_needed()

if __name__ == '__main__':
    app.run(debug=True)
