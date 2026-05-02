from telegram import Update
from telegram.ext import ContextTypes
from keyboards import skip_keyboard, back_keyboard
from db import add_user, update_user_field, get_user
from states import GET_PHOTO, EDIT_CITY, PROFILE
from handlers.profile import get_my_profile_info

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    user = update.effective_user
    await add_user(
        user.id,
        user.username,
        context.user_data['name'],
        context.user_data['sex'],
        context.user_data['age'],
        context.user_data['city'],
        context.user_data['looking_for'],
        )
    await update.message.reply_text(
        'Загрузите фотографию',
        reply_markup=skip_keyboard()
    )

    return GET_PHOTO

async def edit_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Введите новый город',
        reply_markup=back_keyboard()
    )

    return EDIT_CITY

async def update_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update_user_field(update.effective_user.id, 'city', context.user_data['city'])
    user = await get_user(update.effective_user.id)  
    await get_my_profile_info(user, update.message)
    return PROFILE
