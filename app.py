from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import smtplib
import re
import webbrowser

# -----------------------------
# CONTACTS
# -----------------------------
CONTACTS = {
    "mummy gr": "+919391056337",
    "daddy": "+916300714119",
}

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------------
# DATABASE
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# -----------------------------
# LOGIN MANAGER
# -----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -----------------------------
# USER MODEL
# -----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    pin = db.Column(db.String(4))
    role = db.Column(db.String(10))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# -----------------------------
# DATABASE INIT
# -----------------------------
def setup_database():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            user = User(
                username="Bhavya",
                password="1234",
                pin="4321",
                role="user"
            )
            db.session.add(user)
            db.session.commit()

# -----------------------------
# EMAIL SEND
# -----------------------------
def send_email(to_email, subject, body):
    sender_email = "gudurubhavyasri2004@gmail.com"
    app_password = "YOUR_APP_PASSWORD"  # 🔴 paste your app password (no spaces)

    try:
        msg = f"Subject: {subject}\n\n{body}"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg)
        server.quit()
        return True
    except Exception as e:
        print("EMAIL ERROR:", e)
        return False

# -----------------------------
# WHATSAPP
# -----------------------------
def send_whatsapp(number, message):
    try:
        import pywhatkit
        pywhatkit.sendwhatmsg_instantly(number, message, wait_time=10)
        return True
    except Exception as e:
        print("WhatsApp Error:", e)
        return False

# -----------------------------
# LOGIN ROUTE
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        user = User.query.filter(
            db.func.lower(User.username) == username,
            User.password == password
        ).first()

        if user:
            login_user(user)
            return redirect("/dashboard")
        else:
            return "Invalid username or password"

    return render_template("login.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# SEND EMAIL (FORM)
# -----------------------------
@app.route("/send_email", methods=["POST"])
@login_required
def email_route():
    to = request.form["to"]
    subject = request.form["subject"]
    body = request.form["body"]

    if send_email(to, subject, body):
        return "Email Sent"
    return "Failed to send email"

# -----------------------------
# SEND WHATSAPP (FORM)
# -----------------------------
@app.route("/send_whatsapp", methods=["POST"])
@login_required
def whatsapp_route():
    name = request.form["name"].lower()
    message = request.form["message"]
    pin = request.form["pin"]

    if pin != current_user.pin:
        return "Wrong PIN"

    number = CONTACTS.get(name)
    if number:
        send_whatsapp(number, message)
        return "Message Sent"
    return "Contact not found"

# -----------------------------
# 🎤 SMART VOICE ASSISTANT
# -----------------------------
@app.route("/voice-command", methods=["POST"])
@login_required
def voice_command():
    data = request.get_json()
    command = data.get("command").lower()
    pin = data.get("pin")

    print("Voice:", command)

    # 🔐 PIN check
    if pin != current_user.pin:
        return jsonify({"response": "Wrong PIN"})

    # initialize session
    if "step" not in session:
        session["step"] = None

    # -----------------------------
    # STEP 1: START EMAIL
    # -----------------------------
    if "send email" in command:
        session["step"] = "ask_email"
        return jsonify({"response": "To whom should I send the email?"})

    # -----------------------------
    # STEP 2: GET EMAIL
    # -----------------------------
    elif session.get("step") == "ask_email":

        clean = command.replace(" at ", "@").replace(" dot ", ".")
        email_match = re.search(r'\S+@\S+\.\S+', clean)

        if not email_match:
            return jsonify({"response": "Please say a valid email address"})

        session["email"] = email_match.group()
        session["step"] = "ask_message"

        return jsonify({"response": "What is the message?"})

    # -----------------------------
    # STEP 3: GET MESSAGE
    # -----------------------------
    elif session.get("step") == "ask_message":

        to_email = session.get("email")
        message = command

        send_email(to_email, "Voice Email", message)

        session.clear()

        return jsonify({"response": f"Email sent to {to_email}"})

    # -----------------------------
    # WHATSAPP (VOICE)
    # -----------------------------
    elif "message mummy" in command or "send whatsapp" in command:
        send_whatsapp(CONTACTS["mummy gr"], "Hello from voice")
        return jsonify({"response": "Sending message to mummy"})

    elif "message daddy" in command:
        send_whatsapp(CONTACTS["daddy"], "Hello from voice")
        return jsonify({"response": "Sending message to daddy"})

    # -----------------------------
    # OPEN GMAIL
    # -----------------------------
    elif "open gmail" in command:
        webbrowser.open("https://mail.google.com")
        return jsonify({"response": "Opening Gmail"})

    return jsonify({"response": "I did not understand"})

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    setup_database()
    app.run(host="0.0.0.0", port=5000, debug=True)