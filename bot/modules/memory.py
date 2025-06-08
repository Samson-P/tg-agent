import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DATABASE = os.getenv("POSTGRES_DB")

DB_POOL = None

async def init_db():
    global DB_POOL
    DB_POOL = await asyncpg.create_pool(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DATABASE
    )
    async with DB_POOL.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            role TEXT,
            message TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
        """)

async def save_message(user_id, role, message):
    async with DB_POOL.acquire() as conn:
        await conn.execute(
            "INSERT INTO memory (user_id, role, message) VALUES ($1, $2, $3)",
            user_id, role, message
        )

async def get_recent_messages(user_id, limit=10):
    async with DB_POOL.acquire() as conn:
        rows = await conn.fetch(
            "SELECT role, message FROM memory WHERE user_id = $1 ORDER BY timestamp DESC LIMIT $2",
            user_id, limit
        )
        return [{"role": row["role"], "content": row["message"]} for row in reversed(rows)]

