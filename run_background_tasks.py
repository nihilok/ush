import time

from fast_auth import settings

from data.registrations import RegistrationTable
from data.short_urls import ShortURLDatabase

async def delete_expired_registrations():
    db = RegistrationTable(settings.db_path)
    await db.delete_expired_unregistered_users()

async def delete_expired_urls():
    db = ShortURLDatabase(settings.db_path)
    await db.delete_expired_urls(int(time.time()))

async def run_background_tasks():
    await delete_expired_registrations()
    await delete_expired_urls()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_background_tasks())