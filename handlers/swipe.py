from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
from services.swipe import get_next_profile, send_profile, no_more_profiles
from services.match import like_user
from states import SWIPE_MODE
from db import debug_all_users, add_like, add_dislike, get_likes_queue, check_match, save_match, get_user, cleanup_after_match, remove_like
BOT_USERNAME = "kittytestGKh_bot"

# -------------------------
# 🚀 СТАРТ SWIPE
# -------------------------
async def start_swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    filter_data = context.user_data.get("filter", {})

    user = await get_next_profile(user_id, filter_data)

    if not user:
        await update.effective_message.reply_text("😢 Никого больше нет")
        return SWIPE_MODE

    context.user_data["current_profile_id"] = user["id"]

    await send_profile(update, context, user)

    return SWIPE_MODE


# -------------------------
# ❤️ LIKE
# -------------------------
def make_link(user):
    if not user:
        return None

    # dict вариант
    if isinstance(user, dict):
        username = user.get("username")

    # tuple вариант (на случай старых fetchone)
    else:
        try:
            username = user["username"]
        except:
            username = None

    if username:
        return f"https://t.me/{username}"

    return None

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    print("MATCH CHECK START")

    user_id = update.effective_user.id
    target_id = int(query.data.split("_")[1])

    print("LIKE:", user_id, "->", target_id)

    # 1. сохраняем лайк
    await add_like(user_id, target_id)

    # 2. уведомляем пользователя (без падения)
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text="❤️ Вас лайкнули!"
        )
    except Exception as e:
        print("LIKE notify error:", e)

    # 3. проверка матча (ОДИН РАЗ!)
    result = await check_match(user_id, target_id)
    print("CHECK MATCH RESULT:", result)

    if not result:
        return await start_swipe(update, context)

    print("MATCH TRUE")

    # 4. сохраняем матч
    await save_match(user_id, target_id)

    # 5. получаем пользователей
   

    # 9. следующий профиль
    return await start_swipe(update, context)

# -------------------------
# ❌ SKIP
# -------------------------
async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    target_id = int(query.data.split("_")[1])

    print("SKIP:", user_id, "->", target_id)

    await add_dislike(user_id, target_id)
    

    return await start_swipe(update, context)

async def start_likes_queue(update, context):
    user_id = update.effective_user.id

    queue = await get_likes_queue(user_id)

    if not queue:
        await update.effective_message.reply_text("❤️ Пока никто не лайкнул тебя")
        return

    context.user_data["likes_queue"] = queue

    return await show_next_like(update, context)

async def show_next_like(update, context):
    user_id = update.effective_user.id

    # 🔥 ВСЕГДА свежие данные
    queue = await get_likes_queue(user_id)

    if not queue:
        await update.effective_message.reply_text("Ты посмотрел всех 👍")
        return

    context.user_data["likes_queue"] = queue

    user = queue[0]

    context.user_data["current_like_user"] = user["id"]

    caption = f"""
❤️ Тебя лайкнул:
👤 {user['name']}, {user['age']}
📍 {user['city']}
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💖 Лайк", callback_data=f"like_back_{user['id']}"),
            InlineKeyboardButton("❌ Пропустить", callback_data="skip_like")
        ]
    ])

    if user.get("photo"):
        await update.effective_message.reply_photo(
            photo=user["photo"],
            caption=caption,
            reply_markup=keyboard
        )
    else:
        await update.effective_message.reply_text(
            caption,
            reply_markup=keyboard
        )

async def like_back(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    target_id = int(query.data.split("_")[2])

    print("LIKE BACK:", user_id, "->", target_id)

    # ставим лайки с обеих сторон
    await add_like(user_id, target_id)
    await add_like(target_id, user_id)

    # 🔥 MATCH
    if await check_match(user_id, target_id):
        await save_match(user_id, target_id)
        await cleanup_after_match(user_id, target_id)

        user = await get_user(user_id)
        target = await get_user(target_id)

        if user and target:
            link_user = make_link(user)
            link_target = make_link(target)

            await context.bot.send_message(
                chat_id=user_id,
                text=f"💥 МАТЧ с {target['name']}!\n💬 Чат: {link_target or 'нет username'}"
            )

            await context.bot.send_message(
                chat_id=target_id,
                text=f"💥 МАТЧ с {user['name']}!\n💬 Чат: {link_user or 'нет username'}"
            )

    # ✅ удаляем текущего из очереди
    queue = context.user_data.get("likes_queue", [])
    if queue:
        queue.pop(0)

    context.user_data["likes_queue"] = queue

    return await show_next_like(update, context)

async def skip_like(update, context):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    current_user = context.user_data.get("current_like_user")

    if current_user:
        await remove_like(current_user, user_id)   # только удаляем лайк
        # определяем, нужно ли скрывать пользователя в будущем:
        # await hide_user_for_future(user_id, current_user)  # через отдельную таблицу

    queue = context.user_data.get("likes_queue", [])
    if queue:
        queue.pop(0)
    context.user_data["likes_queue"] = queue

    return await show_next_like(update, context)