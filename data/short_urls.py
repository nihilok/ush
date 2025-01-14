import aiosqlite


class ShortURLDatabase:
    def __init__(self, db_path):
        self.db_path = db_path

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS short_urls (
                    key TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    expiry INTEGER
                )
            """
            )
            await db.commit()

    async def insert_url(self, key, url, expiry):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                REPLACE INTO short_urls (key, url, expiry)
                VALUES (?, ?, ?)
            """,
                (key, url, expiry),
            )
            await db.commit()

    async def retrieve_url(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT url FROM short_urls WHERE key = ?
            """,
                (key,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def delete_expired_urls(self, current_time):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                DELETE FROM short_urls WHERE expiry < ?
            """,
                (current_time,),
            )
            await db.commit()


if __name__ == "__main__":
    import asyncio

    from data.constants import DB_PATH

    asyncio.run(ShortURLDatabase(DB_PATH).create_table())
    print("Done!")
