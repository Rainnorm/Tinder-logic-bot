from telegram import Update
from telegram.ext import ContextTypes
from keyboards import back_keyboard
from states import GET_AGE, EDIT_NAME, PROFILE
from db import update_user_field, get_user
from handlers.profile import get_my_profile_info


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        'Введите ваш возраст:',
        reply_markup=back_keyboard()
    )
    return GET_AGE

async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Введите новое имя',
        reply_markup=back_keyboard()
    )

    return EDIT_NAME

async def update_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    pool = context.application.bot_data["pool"]
    await update_user_field(pool, update.effective_user.id, 'name', context.user_data['name'])
    user = await get_user(pool, update.effective_user.id)  
    await get_my_profile_info(user, update.message)
    return PROFILE
