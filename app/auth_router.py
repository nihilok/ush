from fast_auth import User, settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from data.registrations import RegistrationTable
from lib.account_creation import check_existing_registration, email_verification, save_registration, \
    decrypt_verification_link

router = APIRouter()

@router.post("/register/")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    existing_registration = await check_existing_registration(email)
    if existing_registration:
        return {}
    try:
        await User.create(username=form_data.username, password=form_data.password)

    except ValueError as e:
        raise HTTPException(400, str(e))

    await save_registration(email)
    await email_verification(email)

    return {}


@router.get("/verify/{code}/")
async def verify(code: str):
    username = decrypt_verification_link(code)
    await RegistrationTable(settings.user_db_path).delete_by_username(username)
    return {}
