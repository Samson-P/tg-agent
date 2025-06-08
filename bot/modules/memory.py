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
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            UNIQUE(user_id, name)
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


# Новые функции для контактов

async def save_contact(user_id: int, name: str, phone: str = None, email: str = None):
    async with DB_POOL.acquire() as conn:
        await conn.execute("""
            INSERT INTO contacts (user_id, name, phone, email)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, name) DO UPDATE SET phone = EXCLUDED.phone, email = EXCLUDED.email
        """, user_id, name, phone, email)

async def get_contacts(user_id: int):
    async with DB_POOL.acquire() as conn:
        rows = await conn.fetch(
            "SELECT name, phone, email FROM contacts WHERE user_id = $1 ORDER BY name",
            user_id
        )
        return rows

