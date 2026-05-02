from telegram import Update
from telegram.ext import ContextTypes
from keyboards import start_keyboard, back_keyboard
from states import MAIN_MENU, EDIT_ABOUT, PROFILE
from db import save_about, update_user_field, get_user
from handlers.profile import get_my_profile_info


async def get_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    context.user_data['about'] = update.message.text
    await save_about(user.id, context.user_data['about'])
    await update.message.reply_text(
        'Ваши данные сохранены',
        reply_markup=start_keyboard()
    )
    return MAIN_MENU


async def edit_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Введите новое описание',
        reply_markup=back_keyboard()
    )

    return EDIT_ABOUT


async def update_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['about'] = update.message.text
    await update_user_field(update.effective_user.id, 'about', context.user_data['about'])
    user = await get_user(update.effective_user.id)  
    await get_my_profile_info(user, update.message)
    return PROFILE


async def delete_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['about'] = None
    await update_user_field(update.effective_user.id, 'about', context.user_data['about'])
    user = await get_user(update.effective_user.id)  
    await get_my_profile_info(user, query.message)
    return PROFILE