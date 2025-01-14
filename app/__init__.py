import os

from fastapi import FastAPI, Depends, HTTPException
from fast_auth import settings, fast_auth, logged_in_user, User
from starlette.responses import RedirectResponse

from lib.url_shortener import URLShortener

app = FastAPI()

settings.user_db_path = os.getenv("USER_DB_PATH", "users.sqlite3")
settings.secret_key = os.getenv("SECRET_KEY", "SoMeThInG_-sUp3Rs3kREt!!")
settings.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")


fast_auth(app)


@app.post("/")
async def shorten(url: str, user: User = Depends(logged_in_user)):
    return {"url": await URLShortener.shorten(url)}


@app.get("/{key}/")
async def redirect(key: str):
    url = await URLShortener.retrieve(key)
    if url:
        return RedirectResponse(url)
    raise HTTPException(404, "URL not found")
