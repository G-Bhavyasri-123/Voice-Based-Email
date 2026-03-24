import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ---------------- GOOGLE API SCOPES ----------------
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# ---------------- TEXT TO SPEECH ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 150)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


# ---------------- SPEECH TO TEXT ----------------
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak Now...")
        speak("Speak now")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="en-IN")
            print("You said:", text)
            return text.lower()
        except:
            speak("Sorry, I could not understand.")
            return ""


# ---------------- GOOGLE AUTH ----------------
def gmail_authenticate():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


# ---------------- READ PRIMARY EMAILS ----------------
def read_emails(service):
    speak("Reading your latest emails")
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX'], maxResults=5).execute()

    messages = results.get('messages', [])

    if not messages:
        speak("No emails found.")
        return

    for msg in messages:
        txt = service.users().messages().get(
            userId='me', id=msg['id']).execute()

        headers = txt['payload']['headers']
        subject = ""
        sender = ""

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']

        speak(f"Email from {sender}")
        speak(f"Subject is {subject}")


# ---------------- SEND EMAIL ----------------
import base64
import re
from email.mime.text import MIMEText

def send_email(service):
    speak("Please say recipient email address")
    to = listen()

    if not to:
        speak("Email not captured")
        return

    # Convert speech to email format
    to = to.lower()
    to = to.replace(" at ", "@")
    to = to.replace(" dot ", ".")
    to = to.replace(" ", "")

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", to):
        speak("Invalid email format. Please try again.")
        print("Invalid Email:", to)
        return

    print("Final Email:", to)

    speak("Say the subject")
    subject = listen()

    speak("Say the message")
    message_text = listen()

    message = MIMEText(message_text)
    message['To'] = to
    message['From'] = "me"
    message['Subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    body = {'raw': raw}

    try:
        service.users().messages().send(
            userId='me',
            body=body
        ).execute()

        speak("Email sent successfully")

    except Exception as e:
        print("Error:", e)
        speak("Failed to send email")

# ---------------- VOICE ASSISTANT ----------------
def voice_assistant():
    service = gmail_authenticate()

    speak("Welcome to Voice Based Email Assistant")

    while True:
        command = listen()

        if "read email" in command:
            read_emails(service)

        elif "send email" in command:
            send_email(service)

        elif "exit" in command:
            speak("Goodbye")
            break

        else:
            speak("Command not recognized")


# ---------------- LOGIN FUNCTION ----------------
def login():
    username = entry_username.get()
    password = entry_password.get()

    if username == "admin" and password == "1234":
        messagebox.showinfo("Login Success", "Login Successful")
        root.destroy()
        voice_assistant()
    else:
        messagebox.showerror("Login Failed", "Invalid Credentials")


# ---------------- TKINTER LOGIN PAGE ----------------
root = tk.Tk()
root.title("Voice Email Assistant Login")
root.geometry("400x300")

tk.Label(root, text="Voice Email Assistant", font=("Arial", 16)).pack(pady=20)

tk.Label(root, text="Username").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()