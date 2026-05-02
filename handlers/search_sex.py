from telegram import Update
from telegram.ext import ContextTypes
from keyboards import back_keyboard, sex_filter_keyboard
from states import GET_CITY, PROFILE, EDIT_SEARCH_SEX
from handlers.profile import get_my_profile_info
from db import get_user, update_user_field


async def get_search_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'sex_male':
        context.user_data['looking_for'] = 'Мужской'
    elif query.data == 'sex_female':
        context.user_data['looking_for'] = 'Женский'
    else: 
        context.user_data['looking_for'] = 'Все'
    await query.message.reply_text(
        'Введите город',
        reply_markup=back_keyboard()
    )
    return GET_CITY


async def edit_search_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Кто вам интересен?',
        reply_markup=sex_filter_keyboard()
    )

    return EDIT_SEARCH_SEX


async def update_search_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = context.application.bot_data["pool"]
    if query.data == 'sex_male':
        context.user_data['looking_for'] = 'Мужской'
    elif query.data == 'sex_female':
        context.user_data['looking_for'] = 'Женский'
    else: 
        context.user_data['looking_for'] = 'Все'
    await update_user_field(pool, update.effective_user.id, 'looking_for', context.user_data['looking_for'])
    user = await get_user(pool, update.effective_user.id)  
    await get_my_profile_info(user, query.message)
    return PROFILE


