import os

from fastapi import FastAPI, Depends, HTTPException
from fast_auth import settings, fast_auth, logged_in_user, User
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from lib.url_shortener import URLShortener


if os.getenv("USH_DEBUG"):
    docs_url = "/docs"
else:
    docs_url = ""

app = FastAPI(openapi_url=docs_url)


settings.user_db_path = os.getenv("USER_DB_PATH", "users.sqlite3")
settings.secret_key = os.getenv("SECRET_KEY", "SoMeThInG_-sUp3Rs3kREt!!")
settings.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")


fast_auth(app)


class UrlBody(BaseModel):
    url: str


@app.get("/")
async def redirect_to_app():
    ui_url = os.getenv("UI_URL", "http://localhost:5173")
    return RedirectResponse(ui_url)


@app.post("/", dependencies=[Depends(logged_in_user)])
async def shorten(body: UrlBody):
    try:
        return {"url": await URLShortener.shorten(body.url)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/{key}/")
async def redirect(key: str):
    url = await URLShortener.retrieve(key)
    if url:
        return RedirectResponse(url)
    raise HTTPException(404, "URL not found")
