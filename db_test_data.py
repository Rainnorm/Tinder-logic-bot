import asyncio
import aiosqlite

DB_NAME = "bot.db"

TEST_USERS = [
    (1398261530, "alex123", "Alex", 25, "Мужской", "Женский", "Amsterdam", None, "I like coding"),
    (2, "maria99", "Maria", 22, "Женский", "Мужской", "Berlin", None, "Travel lover"),
    (3, "john_dev", "John", 30, "Мужской", "Женский", "Warsaw", None, None),
    (4, "kate_88", "Kate", 27, "Женский", "Мужской", "Prague", None, "Coffee addict"),
    (5, "lin", "lin", 27, "Женский", "Все", "Moscow", None, "Coffee addict"),
    (6, "john", "John12212", 30, "Мужской", "Мужской", "lin", None, None),
    (616927547, "lin", "lin", 27, "Женский", "Все", "Amsterdam", None, "Coffee addict"),
    (8, "mari1212a99", "Mar123ia", 22, "Женский", "Мужской", "Amsterdam", None, "Travel lover"),
    (9, "lin9", "lin", 27, "Женский", "Все", "Amsterdam", None, "Coffee addict"),
    (10, "lin10", "lin", 32, "Мужской", "Все", "Amsterdam", None, "Coffee addict"),
    (11, "lin11", "lin", 30, "Мужской", "Все", "Amsterdam", None, "Coffee addict"),
]


CREATE_TABLE_SQL = """
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
"""





async def seed():
    async with aiosqlite.connect(DB_NAME) as db:
        # создаём таблицу
        await db.execute(CREATE_TABLE_SQL)

        # (ОПЦИОНАЛЬНО) очистка таблицы перед тестом
        await db.execute("DELETE FROM users")

        # вставка тестовых данных
        await db.executemany(
            """
            INSERT INTO users (id, username, name, age, sex, looking_for, city, photo, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            TEST_USERS
        )

        await db.commit()

    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())