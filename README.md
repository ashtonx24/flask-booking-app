# Room Booking System (Flask-based)

A web application to manage room bookings with calendar view, admin panel, email notifications, and export options.

## 📌 Features

- 🔐 User authentication (admin login)
- 📅 Room booking form with time-slot conflict check
- 📤 Booking confirmation via email
- 📊 Admin dashboard to view and cancel bookings
- 📁 Export bookings as CSV
- 📆 Calendar view using FullCalendar.js

## 🛠️ Tech Stack

- Python (Flask)
- SQLite (Database)
- HTML, CSS (Jinja2 templating)
- Flask-Mail (Gmail SMTP)
- FullCalendar.js
- Flask-Login (Authentication)
- dotenv (For env variable management)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ashtonx24/flask-booking-app.git
cd flask-booking-app
```
### 2. Install dependencies
Use a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
### 3. Configure Environment Variables
 Create an `imp.env` file in the root directory:
```bash
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_generated_app_password
```
`Note: Make sure to enable 2FA and use an App Password for Gmail.`

### 4. Run the Application
```bash
python app.py
```

### 👤 Default Admin Credentials

`Username: admin
Password: meowth_admin123
`
`You can edit credentials in USERS dictionary inside app.py.`

### 📂 File Structure
```bash
├── templates/
│   ├── index.html
│   ├── admin.html
│   ├── login.html
│   └── calendar.html
├── app.py
├── bookings.db (auto-created)
├── requirements.txt
├── imp.env
└── README.md
```

---
### ❗Notes
- Booking conflicts are auto-checked by comparing time ranges in the same room.
- Only bookings with an end time in the future are shown in the calendar.

### 📧 Email Functionality
- Booking confirmation emails are sent to the user using Gmail's SMTP server.
- Ensure less secure apps access is enabled or use App Passwords.

### 🧠 Author
- Built by Ashar Parvez Chougle
- Project mentor & AI sidekick: Ashley (ChatGPT)