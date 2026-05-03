
from dotenv import load_dotenv
import os
import asyncpg
import asyncio
DB_NAME = 'bot.db'

load_dotenv()


DB_URL = os.getenv('DB_URL')

async def create_pool():
    return await asyncpg.create_pool(DB_URL)


async def init_db(pool):
    if not DB_URL:
        raise RuntimeError("DB_URL is not set")

    for i in range(15):
        try:
            pool = await asyncpg.create_pool(DB_URL)
            print("DB connected")
            break
        except Exception as e:
            print(f"DB not ready ({i}), retrying...", e)
            await asyncio.sleep(2)

    if pool is None:
        raise RuntimeError("Failed to connect to DB")
    
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username TEXT,
                name TEXT,
                age INTEGER,
                sex TEXT,
                looking_for TEXT,
                city TEXT,
                photo TEXT,
                about TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                update_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                user_id BIGINT,
                target_id BIGINT,
                status INTEGER,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, target_id)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                user1_id BIGINT,
                user2_id BIGINT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user1_id, user2_id)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS views (
                user_id BIGINT,
                target_id BIGINT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, target_id)
            )
        """)
        


async def add_user(pool, user_id, username, name, sex, age, city, looking_for):
    async with pool.acquire() as conn:
        await conn.execute(
                        """
                        INSERT INTO users (id, username, name, sex, age, city, looking_for)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT(id) DO UPDATE SET
                                    username = EXCLUDED.username,
                                    name = EXCLUDED.name,
                                    sex = EXCLUDED.sex,
                                    looking_for = EXCLUDED.looking_for,
                                    age = EXCLUDED.age,
                                    city = EXCLUDED.city,
                                    created_at = NOW(),
                                    update_at = NOW()
                        """,
                        user_id, username, name, sex, age, city, looking_for,)



async def get_user(pool, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, name, age, sex, looking_for, city, photo, about FROM users WHERE id = $1",
            user_id,
        )
        return dict(row) if row else None


async def save_photo(pool, user_id, photo):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (id, photo)
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET
                photo = EXCLUDED.photo,
                update_at = NOW()
            """,
            user_id,
            photo,)



async def save_about(pool, user_id: int, about):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (id, about)
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET
                about = EXCLUDED.about,
                update_at = NOW()
            """,
            user_id,
            about,
        )
        



async def delete_profile(pool, user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM users WHERE id = $1",
            user_id,
        )


async def update_user_field(pool, user_id, field, value):
    allowed_fields = {"sex", "city", "age", "about", "photo", "name", "username", "id", "looking_for"}

    if field not in allowed_fields:
        raise ValueError(f"Invalid field: {field}")

    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO users (id, {field})
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET
                {field} = EXCLUDED.{field},
                update_at = CURRENT_TIMESTAMP
            """,
            user_id,
            value,
        )


async def add_dislike(pool, user_id: int, target_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO likes (user_id, target_id, status)
            VALUES ($1, $2, 0)
            ON CONFLICT (user_id, target_id)
            DO UPDATE SET status = 0
            """,
            user_id,
            target_id,
        )

async def add_like(pool, user_id, target_id):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO likes (user_id, target_id, status)
            VALUES ($1, $2, 1)
            ON CONFLICT (user_id, target_id) DO NOTHING
            """,
            user_id,
            target_id,
        )



async def get_next_user(pool, user_id: int, filter_data: dict):
    min_age = filter_data.get("min_age", 14)
    max_age = filter_data.get("max_age", 100)
    city = filter_data.get("city")

    async with pool.acquire() as conn:

        user = await conn.fetchrow(
            "SELECT sex, looking_for FROM users WHERE id = $1",
            user_id,
        )
        if not user:
            return None

        user_sex = user["sex"]
        user_looking_for = user["looking_for"]

        conditions = [
            "id != $1",
            "age BETWEEN $2 AND $3",
            "id NOT IN (SELECT target_id FROM views WHERE user_id = $4 AND created_at > NOW() - INTERVAL '60 seconds')",
        ]
        params = [user_id, min_age, max_age, user_id]

        if city:
            conditions.append(f"city = ${len(params) + 1}")
            params.append(city)

        if user_looking_for != "Все":
            conditions.append(f"sex = ${len(params) + 1}")
            params.append(user_looking_for)

        conditions.append(
            f"(looking_for = 'Все' OR looking_for = ${len(params) + 1})"
        )
        params.append(user_sex)

        query = (
            "SELECT id, username, name, age, sex, city, photo, about, looking_for "
            "FROM users WHERE " + " AND ".join(conditions) + " ORDER BY RANDOM() LIMIT 1"
        )

        row = await conn.fetchrow(query, *params)
        return dict(row) if row else None


async def remove_like(pool, from_user_id: int, to_user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM likes WHERE user_id = $1 AND target_id = $2",
            from_user_id,
            to_user_id,
        )




async def check_match(pool, user_id: int, target_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT 1
            FROM likes a
            JOIN likes b
              ON a.user_id = b.target_id
             AND a.target_id = b.user_id
             AND a.status = 1
             AND b.status = 1
            WHERE a.user_id = $1
              AND a.target_id = $2
            """,
            user_id,
            target_id,
        )

        print("MATCH DEBUG ROW:", row)

        return row is not None

    
async def get_likes_queue(pool, user_id: int):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT u.id, u.username, u.name, u.age, u.sex, u.city, u.photo, u.about
            FROM likes l
            JOIN users u ON u.id = l.user_id
            WHERE l.target_id = $1
              AND l.status = 1
            ORDER BY l.created_at DESC
            """,
            user_id,
        )
    return [dict(r) for r in rows]

async def save_match(pool, user_id, target_id):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO matches (user1_id, user2_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            user_id,
            target_id,
        )
        await conn.execute(
            """
            INSERT INTO matches (user1_id, user2_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            target_id,
            user_id,
        )

async def cleanup_after_match(pool, user_id: int, target_id: int):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                DELETE FROM likes
                WHERE (user_id = $1 AND target_id = $2)
                   OR (user_id = $2 AND target_id = $1)
                """,
                user_id,
                target_id,
            )

async def remove_like(pool, user_id, target_id):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM likes WHERE user_id = $1 AND target_id = $2",
            user_id,
            target_id,
        )