import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from cryptography.fernet import Fernet

from fast_auth import settings

from data.constants import BASE_URL
from data.registrations import RegistrationTable

# Email templates
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


class AccountCreationService:
    """Service class for handling account creation and verification logic."""

    def __init__(self):
        # Initialize Fernet encryption
        key = os.environ.get("FERNET_KEY")
        if not key:
            raise ValueError("FERNET_KEY environment variable not set")

        self.cipher_suite = Fernet(key)
        self.user_db_path = settings.user_db_path

    async def check_existing_registration(self, username):
        """Check if a username is already registered."""
        db = RegistrationTable(self.user_db_path)
        return await db.retrieve_registration(username)

    async def save_registration(self, username):
        """Save a new registration with an expiry time."""
        expiry = int(time.time()) + 3600  # 1 hour
        db = RegistrationTable(self.user_db_path)
        await db.insert_registration(username, expiry)

    @staticmethod
    def send_verification_email(email, verification_link):
        """Send verification email to the user."""
        sender_email = os.getenv("VERIFY_EMAIL_ADDRESS")
        sender_password = os.getenv("VERIFY_EMAIL_PASSWORD")
        subject = "USH Email Verification"
        body = EMAIL % verification_link

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(os.getenv("MAILSERVER"), 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, email, text)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

    def generate_verification_link(self, username):
        """Generate an encrypted verification link."""
        encrypted_username = self.cipher_suite.encrypt(username.encode()).decode()
        return f"{BASE_URL}verify/{encrypted_username}/"

    def decrypt_username(self, encrypted_username):
        """Decrypt a username from an encrypted verification link."""
        decrypted_username = self.cipher_suite.decrypt(
            encrypted_username.encode()
        ).decode()
        return decrypted_username

    async def email_verification(self, email):
        """Send an email verification link to the user."""
        verification_link = self.generate_verification_link(email)
        self.send_verification_email(email, verification_link)


# Create a singleton instance of the service
_service = AccountCreationService()


# Backward compatibility functions that use the service
async def check_existing_registration(username):
    return await _service.check_existing_registration(username)


async def save_registration(username):
    await _service.save_registration(username)


def send_verification_email(email, verification_link):
    _service.send_verification_email(email, verification_link)


def generate_verification_link(username):
    return _service.generate_verification_link(username)


def decrypt_username(encrypted_username):
    return _service.decrypt_username(encrypted_username)


async def email_verification(email):
    await _service.email_verification(email)
