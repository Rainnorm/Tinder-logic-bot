from telegram import Update
from telegram.ext import ContextTypes
from db import get_user

from handlers.swipe import start_swipe


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = context.application.bot_data["pool"]
    user_id = update.effective_user.id

    user = await get_user(pool, user_id)

    if not user:
        await query.message.reply_text("Сначала заполни профиль")
        return

    # -------------------------
    # 🔥 НОРМАЛИЗУЕМ user (tuple / dict)
    # -------------------------
    if isinstance(user, tuple):
        user = {
            "id": user[0],
            "username": user[1],
            "name": user[2],
            "age": user[3],
            "sex": user[4],
            "looking_for": user[5],
            "city": user[6],
            "photo": user[7],
            "about": user[8]
        }

    # -------------------------
    # 🔥 ФИЛЬТР ИЗ БД (ВАЖНО)
    # -------------------------
    user_age = user["age"]

    # 🔥 диапазон ±3 года
    min_age = max(14, user_age - 3)
    max_age = user_age + 3

    context.user_data["filter"] = {
        "sex": user.get("looking_for"),
        "city": user.get("city"),
        "min_age": min_age,
        "max_age": max_age
    }

    print("FILTER:", context.user_data["filter"])

    return await start_swipe(update, context)