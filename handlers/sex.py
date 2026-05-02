from telegram import Update
from telegram.ext import ContextTypes
from keyboards import sex_keyboard, sex_filter_keyboard
from states import EDIT_SEX, PROFILE, GET_SEARCH_SEX
from handlers.profile import get_my_profile_info
from db import get_user, update_user_field


async def get_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'male':
        context.user_data['sex'] = 'Мужской'
    else:
        context.user_data['sex'] = 'Женский'
    await query.message.reply_text(
        'Кто вам интересен?',
        reply_markup=sex_filter_keyboard()
    )
    return GET_SEARCH_SEX


async def edit_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Выберите пол',
        reply_markup=sex_keyboard()
    )

    return EDIT_SEX


async def update_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = context.application.bot_data["pool"]
    if query.data == 'male':
        context.user_data['sex'] = 'Мужской'
    else:
        context.user_data['sex'] = 'Женский'
    await update_user_field(pool, update.effective_user.id, 'sex', context.user_data['sex'])
    user = await get_user(pool, update.effective_user.id)  
    await get_my_profile_info(user, query.message)
    return PROFILE


