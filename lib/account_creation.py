import time

from fast_auth import settings

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

async def email_verification(email):
    # Send email verification link to the user
    pass
