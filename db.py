import aiosqlite

DB_NAME = 'bot.db'


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY,
                         username TEXT,
                         name TEXT,
                         age INTEGER,
                         sex TEXT,
                         looking_for TEXT,
                         city TEXT,
                         photo TEXT,
                         about TEXT,
                         created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                         update_at DATETIME DEFAULT CURRENT_TIMESTAMP

            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                        user_id INTEGER,
                        target_id INTEGER,
                        status INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, target_id)
                    )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                user1_id INTEGER,
                user2_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user1_id, user2_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS views (
                user_id INTEGER,
                target_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, target_id)
            )
        """)
        
        await db.commit()


async def add_user(user_id, username, name, sex, age, city, looking_for):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
                        """
                        INSERT INTO users (id, username, name, sex, age, city, looking_for)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                                    username = excluded.username,
                                    name = excluded.name,
                                    sex = excluded.sex,
                                    looking_for = excluded.looking_for,
                                    age = excluded.age,
                                    city = excluded.city,
                                    created_at = CURRENT_TIMESTAMP,
                                    update_at = CURRENT_TIMESTAMP
                        """,
                        (user_id, username, name, sex, age, city, looking_for)
                        )
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row  # 🔥 ВАЖНО

        cursor = await db.execute(
            "SELECT id, username, name, age, sex, looking_for, city, photo, about FROM users WHERE id = ?",
            (user_id,)
        )

        row = await cursor.fetchone()

        if not row:
            return None

        return dict(row)


async def save_photo(user_id, photo):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO users (id, photo)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET
                            photo = excluded.photo,
                            update_at = CURRENT_TIMESTAMP
            """,
            (user_id, photo)
        )

        await db.commit()


async def save_about(user_id: int, about):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO users (id, about)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET
                            about = excluded.about,
                            update_at = CURRENT_TIMESTAMP
            """,
            (user_id, about)
        )

        await db.commit()


async def delete_profile(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM users WHERE id = ?;",
            (int(user_id),)
        )
        await db.commit()


async def update_user_field(user_id, field, value):
    allowed_fields = {"sex", "city", "age", 'about', 'photo', 'name', 'username', 'id' , 'looking_for'}

    if field not in allowed_fields:
        raise ValueError(f"Invalid field: {field}")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            f"""
            INSERT INTO users (id, {field})
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET
                {field} = excluded.{field},
                update_at = CURRENT_TIMESTAMP
            """,
            (user_id, value)
        )
        await db.commit()


########################################################################################################################################################################################
########################################################################################################################################################################################
########################################################################################################################################################################################
########################################################################################################################################################################################
########################################################################################################################################################################################
async def debug_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, sex, age, city FROM users") as cursor:
            rows = await cursor.fetchall()
            print("ALL USERS:", rows)


async def add_dislike(user_id: int, target_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO likes (user_id, target_id, status)
            VALUES (?, ?, 0)
            ON CONFLICT(user_id, target_id)
            DO UPDATE SET status = 0
            """,
            (user_id, target_id)
        )
        await db.commit()

async def add_like(user_id, target_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO likes (user_id, target_id, status)
            VALUES (?, ?, 1)
        """, (user_id, target_id))

        await db.commit()  # 🔥 ОБЯЗАТЕЛЬНО



async def get_next_user(user_id: int, filter_data: dict):
    min_age = filter_data.get("min_age", 14)
    max_age = filter_data.get("max_age", 100)
    city = filter_data.get("city")

    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT sex, looking_for FROM users WHERE id = ?",
            (user_id,)
        )
        user = await cursor.fetchone()

        if not user:
            return None

        user_sex = user["sex"]
        user_looking_for = user["looking_for"]

        query = """
        SELECT id, username, name, age, sex, city, photo, about, looking_for
        FROM users
        WHERE id != ?
          AND age BETWEEN ? AND ?
          AND id NOT IN (
                SELECT target_id
                FROM views
                WHERE user_id = ?
                AND datetime(created_at) > datetime('now', '-10 seconds')
          )
        """

        params = [user_id, min_age, max_age, user_id]

        # город
        if city:
            query += " AND city = ?"
            params.append(city)

        # кого ищет пользователь
        if user_looking_for != "Все":
            query += " AND sex = ?"
            params.append(user_looking_for)

        # взаимность
        query += """
        AND (
            looking_for = 'Все'
            OR looking_for = ?
        )
        """
        params.append(user_sex)

        query += " ORDER BY RANDOM() LIMIT 1"

        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()

        return dict(row) if row else None



async def save_like(from_user_id: int, to_user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO likes (from_user_id, target_id)
            VALUES (?, ?)
            """,
            (from_user_id, to_user_id)
        )
        await db.commit()


# 🔍 проверить, лайкнул ли один пользователь другого
async def check_like(from_user_id: int, to_user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT 1 FROM likes
            WHERE from_user_id = ? AND target_id = ?
            """,
            (from_user_id, to_user_id)
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


# 💘 проверить взаимный лайк (мэтч)
async def is_match(user1_id: int, user2_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT 1 FROM likes
            WHERE (from_user_id = ? AND target_id = ?)
               OR (from_user_id = ? AND target_id = ?)
            """,
            (user1_id, user2_id, user2_id, user1_id)
        ) as cursor:
            rows = await cursor.fetchall()

            # должно быть 2 лайка (в обе стороны)
            return len(rows) == 2


# 💣 удалить лайк (если понадобится skip/undo)
async def remove_like(from_user_id: int, to_user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            DELETE FROM likes
            WHERE from_user_id = ? AND target_id = ?
            """,
            (from_user_id, to_user_id)
        )
        await db.commit()


# 📊 получить всех, кого лайкнул пользователь
async def get_likes_sent(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT target_id FROM likes
            WHERE from_user_id = ?
            """,
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()
        

async def create_match(user1_id: int, user2_id: int):
    """
    Создаёт мэтч между двумя пользователями
    (всегда хранит в порядке min/max чтобы не было дублей)
    """
    user_a = min(user1_id, user2_id)
    user_b = max(user1_id, user2_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO matches (user1_id, user2_id)
            VALUES (?, ?)
            """,
            (user_a, user_b)
        )
        await db.commit()


async def is_match(user1_id: int, user2_id: int) -> bool:
    """
    Проверяет, есть ли взаимный мэтч
    """
    user_a = min(user1_id, user2_id)
    user_b = max(user1_id, user2_id)

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT 1 FROM matches
            WHERE user1_id = ? AND user2_id = ?
            """,
            (user_a, user_b)
        ) as cursor:
            return await cursor.fetchone() is not None
        
async def get_matches(user_id: int):
    """
    Возвращает список всех мэтчей пользователя
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT user1_id, user2_id
            FROM matches
            WHERE user1_id = ? OR user2_id = ?
            """,
            (user_id, user_id)
        ) as cursor:
            rows = await cursor.fetchall()

    # превращаем в "второго участника"
    matches = []
    for user1, user2 in rows:
        match_id = user2 if user1 == user_id else user1
        matches.append(match_id)

    return matches


async def remove_match(user1_id: int, user2_id: int):
    """
    Удаляет мэтч (например, если блокировка/анлайк)
    """
    user_a = min(user1_id, user2_id)
    user_b = max(user1_id, user2_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            DELETE FROM matches
            WHERE user1_id = ? AND user2_id = ?
            """,
            (user_a, user_b)
        )
        await db.commit()

async def check_match(user_id: int, target_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT 1
            FROM likes a
            JOIN likes b
            ON a.user_id = b.target_id
            AND a.target_id = b.user_id
            WHERE a.user_id = ?
            AND a.target_id = ?
        """, (user_id, target_id))

        row = await cursor.fetchone()

        print("MATCH DEBUG ROW:", row)

        return row is not None

    
async def get_likes_queue(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
            SELECT u.id, u.username, u.name, u.age, u.sex, u.city, u.photo, u.about
            FROM likes l
            JOIN users u ON u.id = l.user_id
            WHERE l.target_id = ?
            ORDER BY l.created_at DESC
        """, (user_id,))

        rows = await cursor.fetchall()

    return [dict(r) for r in rows]

async def save_match(user_id, target_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO matches (user1_id, user2_id)
            VALUES (?, ?)
        """, (user_id, target_id))

        await db.execute("""
            INSERT OR IGNORE INTO matches (user1_id, user2_id)
            VALUES (?, ?)
        """, (target_id, user_id))

        await db.commit()

async def cleanup_after_match(user_id: int, target_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        # удалить лайки
        await db.execute("""
            DELETE FROM likes
            WHERE (user_id = ? AND target_id = ?)
               OR (user_id = ? AND target_id = ?)
        """, (user_id, target_id, target_id, user_id))

        # удалить дизлайки (если есть таблица)


        await db.commit()

async def remove_like(user_id, target_id):
    async with aiosqlite.connect(DB_NAME) as db:
        query = """
        DELETE FROM likes
        WHERE user_id = ? AND target_id = ?
        """
        await db.execute(query, (user_id, target_id))
        await db.commit()