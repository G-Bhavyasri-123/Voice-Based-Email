import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import smtplib
import imaplib
import email
from email.mime.text import MIMEText


# TEXT TO SPEECH 
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()


#  SPEECH TO TEXT 
def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Speak Now...")
        speak("Speak now")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        print("You said:", text)
        return text.lower()
    except:
        speak("Sorry I could not understand")
        return ""


# SEND EMAIL FUNCTION 
def send_email():
    speak("Tell me the receiver email address")
    receiver = listen()

    speak("Tell me the subject")
    subject = listen()

    speak("Tell me the message")
    message = listen()

    try:
        msg = MIMEText(message)
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver
        msg["Subject"] = subject

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver, msg.as_string())
        server.quit()

        speak("Email sent successfully")
        print("Email sent successfully")

    except Exception as e:
        speak("Failed to send email")
        print("Error:", e)


# READ EMAIL FUNCTION 
def read_email():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        latest_email_id = mail_ids[-1]
        result, data = mail.fetch(latest_email_id, "(RFC822)")

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg["subject"]
        from_ = msg["from"]

        speak("Latest email is from " + from_)
        speak("Subject is " + subject)

        print("From:", from_)
        print("Subject:", subject)

        mail.logout()

    except Exception as e:
        speak("Unable to read email")
        print("Error:", e)


# VOICE ASSISTANT 
def voice_assistant():
    speak("Welcome to Voice Based Email Assistant. Milestone two started.")

    while True:
        command = listen()

        if "send email" in command:
            send_email()

        elif "read email" in command:
            read_email()

        elif "exit" in command or "bye" in command:
            speak("Goodbye")
            break

        else:
            speak("Command not available")


#  LOGIN FUNCTION 
def login():
    global EMAIL_ADDRESS, EMAIL_PASSWORD

    EMAIL_ADDRESS = entry_username.get()
    EMAIL_PASSWORD = entry_password.get()

    if EMAIL_ADDRESS != "" and EMAIL_PASSWORD != "":
        messagebox.showinfo("Login Success", "Login Successful")
        speak("Login successful")
        root.destroy()
        voice_assistant()
    else:
        messagebox.showerror("Error", "Enter valid credentials")


# TKINTER LOGIN PAGE 
root = tk.Tk()
root.title("Voice Email Assistant Login")
root.geometry("400x300")
root.configure(bg="#e6f7ff")

tk.Label(root, text="Voice Email Assistant",
         font=("Arial", 18, "bold"),
         bg="#e6f7ff").pack(pady=20)

tk.Label(root, text="Gmail Address",
         bg="#e6f7ff").pack()

entry_username = tk.Entry(root, width=30)
entry_username.pack(pady=5)

tk.Label(root, text="App Password",
         bg="#e6f7ff").pack()

entry_password = tk.Entry(root, show="*", width=30)
entry_password.pack(pady=5)

tk.Button(root, text="Login",
          bg="green", fg="white",
          command=login).pack(pady=20)

root.mainloop()