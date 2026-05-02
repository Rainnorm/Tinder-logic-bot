from telegram import Update
from telegram.ext import ContextTypes
from keyboards import start_keyboard
from states import MAIN_MENU, PROFILE
from handlers.profile import get_my_profile_info
from db import get_user


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == 'cancel':
            await query.message.reply_text(
                'Действие отменено\nВыберите действие:',
                reply_markup=start_keyboard()
            )
    else:
        await update.message.reply_text(
                'Отменено',
                reply_markup=start_keyboard()
            )
    return MAIN_MENU


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = context.application.bot_data["pool"]
    user = await get_user(pool, update.effective_user.id)
    await get_my_profile_info(user, query.message)

    return PROFILE