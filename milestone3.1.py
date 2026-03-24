from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import smtplib
import re
import webbrowser
import base64

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


#  DATABASE 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#  LOGIN

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username,password=password).first()

        if user:
            login_user(user)
            return redirect("/dashboard")

    return render_template("login.html")


# REGISTER 

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        new_user = User(username=username,password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


#  DASHBOARD 

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html",user=current_user.username)


# EMAIL SEND 

def send_email(receiver,message):

    sender = "yourgmail@gmail.com"
    password = "your_app_password"

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()

    server.login(sender,password)

    email = f"Subject: Voice Mail\n\n{message}"

    server.sendmail(sender,receiver,email)

    server.quit()


#  REAL EMAIL READER 

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def read_email():

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)

    creds = flow.run_local_server(port=0)

    service = build('gmail','v1',credentials=creds)

    results = service.users().messages().list(
        userId='me', maxResults=1).execute()

    messages = results.get('messages', [])

    if not messages:
        return "No emails found"

    msg = service.users().messages().get(
        userId='me', id=messages[0]['id']).execute()

    payload = msg['payload']
    headers = payload['headers']

    subject = ""
    sender = ""

    for header in headers:

        if header['name'] == 'Subject':
            subject = header['value']

        if header['name'] == 'From':
            sender = header['value']

    return f"Email from {sender}. Subject: {subject}"

#  WHATSAPP 
contacts = {
    "Mummy GR":{"phone":"9391056337"}
}

def send_whatsapp(name,message):

    name = name.lower()

    if name in contacts:

        phone = contacts[name]["phone"]

        url = f"https://wa.me/91{phone}?text={message}"

        webbrowser.open(url)

        return "Opening WhatsApp chat"

    else:

        return "Contact not found"


# VOICE COMMAND 

pending_email = {}

@app.route("/process_command",methods=["POST"])
@login_required
def process_command():

    global pending_email

    text = request.json["text"].lower()


    # SEND EMAIL

    if "send mail to" in text:

        match = re.search(r"send mail to (.+?) saying (.+)",text)

        if match:

            receiver = match.group(1)
            message = match.group(2)

            pending_email = {
            "receiver":receiver,
            "message":message
            }

            return jsonify({
            "reply":f"Do you want to send email to {receiver}? say yes to confirm"
            })


    # CONFIRM EMAIL

    if pending_email != {}:

        if "yes" in text:

            send_email(
            pending_email["receiver"],
            pending_email["message"]
            )

            pending_email = {}

            return jsonify({"reply":"Email sent successfully"})


    # READ EMAIL

    if "read email" in text:

        email = read_email()

        return jsonify({"reply":email})


    # WHATSAPP

    if "send whatsapp message to" in text:

        match = re.search(r"send whatsapp message to (.+?) saying (.+)",text)

        if match:

            name = match.group(1)
            message = match.group(2)

            result = send_whatsapp(name,message)

            return jsonify({"reply":result})


    return jsonify({"reply":"Command not recognized"})


# ---------------- LOGOUT ----------------

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


#  RUN 

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)