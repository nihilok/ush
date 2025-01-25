import time

import aiosqlite


class RegistrationTable:
    def __init__(self, db_path):
        self.db_path = db_path

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS registration (
                    username TEXT PRIMARY KEY,
                    expiry INTEGER
                )
            """
            )
            await db.commit()

    async def check_table_exists(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT name FROM sqlite_master WHERE type='table' AND name='registration'
            """
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None


    async def insert_registration(self, username, expiry):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                REPLACE INTO registration (username, expiry)
                VALUES (?, ?)
            """,
                (username, expiry),
            )
            await db.commit()

    async def retrieve_registration(self, username):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT expiry FROM registration WHERE username = ?
            """,
                (username,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def delete_expired_registrations_returning_usernames(self, current_time):

        statement = """
                DELETE FROM registration WHERE expiry < ? RETURNING username
            """

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                statement,
                (current_time,),
            ) as cursor:
                rows = await cursor.fetchall()
                await db.commit()
                return [row[0] for row in rows]

    async def delete_expired_unregistered_users(self):
        expired_registrations = await self.delete_expired_registrations_returning_usernames(int(time.time()))
        if not expired_registrations:
            return

        arr = "(" + ",".join(["?" for _ in expired_registrations]) + ")"

        statement = """DELETE FROM users WHERE username NOT IN {};""".format(arr)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(statement, expired_registrations)
            await db.commit()

    async def delete_by_username(self, username):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                DELETE FROM registration WHERE username = ? RETURNING username
            """,
                (username,),
            ) as cursor:
                rows = await cursor.fetchall()
                await db.commit()
                return not not rows

if __name__ == "__main__":
    import asyncio

    from fast_auth import settings

    asyncio.run(RegistrationTable(settings.user_db_path).create_table())
    print("Done!")