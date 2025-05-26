from ics import Calendar, Event
from flask import send_file
import tempfile
import datetime
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from flask import Response
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask import jsonify
from datetime import datetime
load_dotenv(dotenv_path='imp.env')


app = Flask(__name__)


# --- Flask-Mail Config ---
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

app.secret_key = 'a_very_strong_and_random_secret_key_123!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# --- Configuration ---

DB_FILE = 'bookings.db'

class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash

USERS = {
    "admin": User(1, "admin", generate_password_hash("meowth_admin123")),
}

@login_manager.user_loader
def load_user(user_id):
    for user in USERS.values():
        if str(user.id) == user_id:
            return user
    return None


# --- Database Setup ---
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                room TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()


# Run once at app start
init_db()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    room = request.form['room']
    start = request.form['start']
    end = request.form['end']
    email = request.form['email']

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Overlap check
    c.execute('''SELECT COUNT(*) FROM bookings WHERE room = ? AND (start < ? AND end > ?)''', (room, end, start))
    (overlap_count,) = c.fetchone()
    if overlap_count > 0:
        conn.close()
        return "Room already booked for that time slot", 400

    c.execute('INSERT INTO bookings (name, room, start, end) VALUES (?, ?, ?, ?)', (name, room, start, end))
    conn.commit()
    conn.close()

    # Send confirmation email...
    # (Your existing mail sending code here)
    # Send confirmation email
    msg = Message(
        subject='Booking Confirmation', recipients=[email],
                  sender=os.getenv('MAIL_USERNAME'))
    msg.body = f"Hi {name}, your booking for {room} from {start} to {end} is confirmed."
    mail.send(msg)

    return redirect(url_for('index'))

## for the admin page
@app.route('/admin')
@login_required
def admin():
    print(f"DEBUG: current_user.is_authenticated = {current_user.is_authenticated}")
    if not current_user.is_authenticated:
        return "Not logged in — access denied!", 403
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM bookings ORDER BY start')
    all_bookings = c.fetchall()
    conn.close()
    return render_template('admin.html', bookings=all_bookings)

## login and logout functionality
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin')
            return redirect(next_page)
        else:
            return "Invalid credentials", 403
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

## Booking cancellation functionality
@app.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# export route
@app.route('/export')
@login_required
def export_bookings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM bookings ORDER BY start')
    bookings = c.fetchall()
    conn.close()

    def generate():
        yield 'ID,Name,Room,Start,End\n'
        for row in bookings:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=bookings.csv'})

# @app.route('/calendar/<int:booking_id>')
# @login_required
# def download_ics(booking_id):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute('SELECT name, room, start, end FROM bookings WHERE id = ?', (booking_id,))
#     result = c.fetchone()
#     conn.close()

#     if not result:
#         return "Booking not found", 404

#     name, room, start, end = result

#     # Parse to datetime objects
#     start_dt = datetime.datetime.fromisoformat(start)
#     end_dt = datetime.datetime.fromisoformat(end)

#     # Create calendar event
#     cal = Calendar()
#     event = Event()
#     event.name = f"{room} Booking - {name}"
#     event.begin = start_dt
#     event.end = end_dt
#     event.location = "Your lodging location"  # Optional
#     event.description = f"Room: {room}\nBooked by: {name}"
#     cal.events.add(event)

#     # Write to temporary file
#     with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.ics') as f:
#         f.write(str(cal))
#         f.seek(0)
#         return send_file(f.name, as_attachment=True, download_name=f"{room}_booking.ics")
    
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login') + '?next=' + request.path)


# This is the main route for the calendar view
@app.route('/calendar-view')
@login_required
def calendar_view():
    return render_template('calendar.html')

# calendar data route for FullCalendar
@app.route('/calendar-data')
@login_required
def calendar_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.now().isoformat(timespec='seconds')
    c.execute("SELECT name, room, start, end FROM bookings WHERE end >= ?", (today,))
    rows = c.fetchall()
    conn.close()

    # Return events formatted for FullCalendar
    events = [{
        "title": f"{room} - {name}",
        "start": start,
        "end": end
    } for name, room, start, end in rows]

    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
