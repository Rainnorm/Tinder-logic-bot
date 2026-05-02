from telegram import Update
from telegram.ext import ContextTypes
from keyboards import skip_keyboard, back_keyboard
from states import GET_ABOUT, EDIT_PHOTO, PROFILE
from db import save_photo, update_user_field, get_user
from handlers.profile import get_my_profile_info


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo'] = update.message.photo[-1].file_id
    user = update.effective_user
    await save_photo(user.id, context.user_data['photo'])
    await update.message.reply_text(
        'Расскажите о себе',
        reply_markup=skip_keyboard()
    )

    return GET_ABOUT

async def edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Загрузите новое фото',
        reply_markup=back_keyboard()
    )

    return EDIT_PHOTO


async def update_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo'] = update.message.photo[-1].file_id
    await update_user_field(update.effective_user.id, 'photo', context.user_data['photo'])
    user = await get_user(update.effective_user.id)  
    await get_my_profile_info(user, update.message)
    return PROFILE


async def delete_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['photo'] = None
    await update_user_field(update.effective_user.id, 'photo', context.user_data['photo'])
    user = await get_user(update.effective_user.id)  
    await get_my_profile_info(user, query.message)
    return PROFILE