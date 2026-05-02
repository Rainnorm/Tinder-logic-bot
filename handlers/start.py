from telegram import Update
from telegram.ext import ContextTypes
from keyboards import start_keyboard
from states import MAIN_MENU
from db import get_user, update_user_field

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.application.bot_data["pool"]
    user = await get_user(pool, update.effective_user.id)
    if user:
        await update_user_field(pool, update.effective_user.id, 'username', update.effective_user.username)
    await update.message.reply_text(
        "Добро пожаловать!\nВыберите действие:",
        reply_markup=start_keyboard()
        )
    return MAIN_MENU