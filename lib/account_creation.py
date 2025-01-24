import hashlib
import os
import time

from fast_auth import settings

from cli import BASE_URL
from data.registrations import RegistrationTable


async def check_existing_registration(username):
    # Check if the username already exists in the database
    db = RegistrationTable(settings.user_db_path)
    return await db.retrieve_registration(username)

async def save_registration(username):
    # Save the registration details to the database
    expiry = int(time.time()) + 3600 # 1 hour
    db = RegistrationTable(settings.user_db_path)
    await db.insert_registration(username, expiry)


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = """
Thanks for creating an USH account! To verify your email address, please click the following link:

%s

If you do nothing, your account will be removed in 1-2 hours, and your data will be removed from the system.

USH Team
"""


def send_verification_email(email, verification_link):
    sender_email = os.getenv("VERIFY_EMAIL_ADDRESS")
    sender_password = os.getenv("VERIFY_EMAIL_PASSWORD")
    subject = "USH Email Verification"
    body = EMAIL % verification_link

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


def generate_verification_link(username):
    salt = os.environ["USH_SALT"]
    username = f"{username}{salt}"
    username_hash = hashlib.sha256(username.encode()).hexdigest()
    return f"{BASE_URL}/verify/{username_hash}/"


def decrypt_verification_link(username_hash):
    salt = os.environ["USH_SALT"]
    username = hashlib.sha256(username_hash.encode()).hexdigest()
    return username[:-len(salt)]

async def email_verification(email):
    # Send email verification link to the user
    verification_link = generate_verification_link(email)
    send_verification_email(email, verification_link)
