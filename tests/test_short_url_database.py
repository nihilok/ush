import time
from pathlib import Path

import pytest
import aiosqlite
from data.short_urls import ShortURLDatabase



@pytest.fixture(scope="function", autouse=True)
def sqlite_db_file(tmp_path):
    db_path = Path(__file__).parent / f"test_db_{time.time()}.sqlite"
    yield db_path
    db_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_create_table_creates_table(sqlite_db_file):
    db = ShortURLDatabase(sqlite_db_file)
    await db.create_table()
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='short_urls'")
        table = await cursor.fetchone()
        assert table is not None

@pytest.mark.asyncio
async def test_insert_url_inserts_url(sqlite_db_file):
    db = ShortURLDatabase(sqlite_db_file)
    await db.create_table()
    await db.insert_url("test_key", "https://example.com", 1234567890)
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT url FROM short_urls WHERE key='test_key'")
        row = await cursor.fetchone()
        assert row[0] == "https://example.com"

@pytest.mark.asyncio
async def test_retrieve_url_returns_correct_url(sqlite_db_file):
    db = ShortURLDatabase(sqlite_db_file)
    await db.create_table()
    await db.insert_url("test_key", "https://example.com", 1234567890)
    url = await db.retrieve_url("test_key")
    assert url == "https://example.com"

@pytest.mark.asyncio
async def test_retrieve_url_returns_none_for_nonexistent_key(sqlite_db_file):
    db = ShortURLDatabase(sqlite_db_file)
    await db.create_table()
    url = await db.retrieve_url("nonexistent_key")
    assert url is None

@pytest.mark.asyncio
async def test_delete_expired_urls_deletes_expired_urls(sqlite_db_file):
    db = ShortURLDatabase(sqlite_db_file)
    await db.create_table()
    await db.insert_url("expired_key", "https://expired.com", 1234567890)
    await db.insert_url("valid_key", "https://valid.com", 9999999999)
    await db.delete_expired_urls(2000000000)
    async with aiosqlite.connect(db.db_path) as conn:
        cursor = await conn.execute("SELECT url FROM short_urls WHERE key='expired_key'")
        expired_row = await cursor.fetchone()
        cursor = await conn.execute("SELECT url FROM short_urls WHERE key='valid_key'")
        valid_row = await cursor.fetchone()
        assert expired_row is None
        assert valid_row[0] == "https://valid.com"
