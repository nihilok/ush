import os
import time

from fast_auth import settings

from data.constants import BASE_URL
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

VERIFICATION_PAGE = """\
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Email verified!</h1>
    <a href="/">Home</a>
</body>
</html>
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
        server = smtplib.SMTP(os.getenv("MAILSERVER"), 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


from cryptography.fernet import Fernet

# Generate a key for encryption and decryption
# You should store this key securely and not regenerate it every time
key = os.environ.get("FERNET_KEY")
if not key:
    key = Fernet.generate_key()
    os.environ["FERNET_KEY"] = key.decode()

cipher_suite = Fernet(key)

def generate_verification_link(username):
    encrypted_username = cipher_suite.encrypt(username.encode()).decode()
    return f"{BASE_URL}verify/{encrypted_username}/"


def decrypt_username(encrypted_username):
    decrypted_username = cipher_suite.decrypt(encrypted_username.encode()).decode()
    return decrypted_username

async def email_verification(email):
    # Send email verification link to the user
    verification_link = generate_verification_link(email)
    send_verification_email(email, verification_link)
