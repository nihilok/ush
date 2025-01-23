import time
from pathlib import Path

import pytest
import aiosqlite
from data.registrations import RegistrationTable


@pytest.fixture(scope="function", autouse=True)
def sqlite_db_file(tmp_path):
    db_path = Path(__file__).parent / f"test_db_{time.time()}.sqlite"
    yield db_path
    db_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_create_table_creates_table(sqlite_db_file):
    db = RegistrationTable(sqlite_db_file)
    await db.create_table()
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registration'")
        table = await cursor.fetchone()
        assert table is not None

@pytest.mark.asyncio
async def test_insert_registration_inserts_registration(sqlite_db_file):
    db = RegistrationTable(sqlite_db_file)
    await db.create_table()
    await db.insert_registration("test_user", 1234567890)
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT expiry FROM registration WHERE username='test_user'")
        row = await cursor.fetchone()
        assert row[0] == 1234567890

@pytest.mark.asyncio
async def test_retrieve_registration_returns_correct_expiry(sqlite_db_file):
    db = RegistrationTable(sqlite_db_file)
    await db.create_table()
    await db.insert_registration("test_user", 1234567890)
    expiry = await db.retrieve_registration("test_user")
    assert expiry == 1234567890

@pytest.mark.asyncio
async def test_retrieve_registration_returns_none_for_nonexistent_user(sqlite_db_file):
    db = RegistrationTable(sqlite_db_file)
    await db.create_table()
    expiry = await db.retrieve_registration("nonexistent_user")
    assert expiry is None

@pytest.mark.asyncio
async def test_delete_expired_registrations_deletes_expired_registrations(sqlite_db_file):
    db = RegistrationTable(sqlite_db_file)
    await db.create_table()
    await db.insert_registration("expired_user", 1234567890)
    await db.insert_registration("valid_user", 9999999999)
    deleted_usernames = await db.delete_expired_registrations_returning_usernames(2000000000)
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT username FROM registration WHERE username='expired_user'")
        expired_row = await cursor.fetchone()
        cursor = await conn.execute("SELECT username FROM registration WHERE username='valid_user'")
        valid_row = await cursor.fetchone()
        assert expired_row is None
        assert valid_row[0] == "valid_user"
        assert "expired_user" in deleted_usernames
        assert "valid_user" not in deleted_usernames