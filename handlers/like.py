from services.match import like_user
from handlers.swipe import start_swipe
from telegram import Updatet
from db import add_like, get_user, check_match
from telegram.ext import ContextTypes
from telegram.error import Forbidden

BOT = None  # будет установлен при старте

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # 🔥 берём ID из callback_data
    target_id = int(query.data.split("_")[1])

    print("LIKE:", user_id, "->", target_id)

    await add_like(user_id, target_id)

    return await start_swipe(update, context)