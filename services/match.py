from db import save_like, check_like, get_user, create_match

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# -----------------------------
# 💘 ОБРАБОТКА ЛАЙКА
# -----------------------------
async def process_like(context, from_user_id: int, to_user_id: int):
    """
    Главная функция лайка:
    1. сохраняет лайк
    2. проверяет взаимность
    3. создаёт матч
    4. отправляет уведомления
    """

    # 1. сохраняем лайк
    await save_like(from_user_id, to_user_id)

    # 2. проверяем обратный лайк
    is_mutual = await check_like(to_user_id, from_user_id)

    # 3. если есть взаимность → матч
    if is_mutual:
        await create_match(from_user_id, to_user_id)

        await notify_match(context, from_user_id, to_user_id)

        return True

    return False


# -----------------------------
# 💬 УВЕДОМЛЕНИЕ О МЭТЧЕ
# -----------------------------
async def notify_match(context, user1_id: int, user2_id: int):
    """
    Отправляет уведомление обоим пользователям
    """

    user1 = await get_user(user1_id)
    user2 = await get_user(user2_id)

    # кнопка "перейти в чат"
    keyboard1 = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Написать", callback_data=f"chat_{user2_id}")]
    ])

    keyboard2 = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Написать", callback_data=f"chat_{user1_id}")]
    ])

    text1 = f"💘 У тебя мэтч с {user2[2]}!"
    text2 = f"💘 У тебя мэтч с {user1[2]}!"

    # user1 уведомление
    await context.bot.send_message(
        chat_id=user1_id,
        text=text1,
        reply_markup=keyboard1
    )

    # user2 уведомление
    await context.bot.send_message(
        chat_id=user2_id,
        text=text2,
        reply_markup=keyboard2
    )


# -----------------------------
# 👍 ЛАЙК (обёртка для handler)
# -----------------------------
async def like_user(context, from_user_id: int, to_user_id: int):
    """
    Вызывается из handlers
    """

    is_match = await process_like(context, from_user_id, to_user_id)

    return is_match


# -----------------------------
# ❌ СКИП (если нужно расширить потом)
# -----------------------------
async def skip_user(from_user_id: int, to_user_id: int):
    """
    Можно расширить:
    - blacklist
    - cooldown
    - скрытие пользователя
    """
    pass