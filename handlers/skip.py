from telegram import Update
from telegram.ext import ContextTypes
from keyboards import start_keyboard, skip_keyboard
from states import MAIN_MENU, GET_ABOUT

async def skip_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        'Сохранено',
        reply_markup=start_keyboard()
    )
    return MAIN_MENU

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        'Расскажите о себе:',
        reply_markup=skip_keyboard()
    )
    return GET_ABOUT