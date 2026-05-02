from telegram import Update
from telegram.ext import ContextTypes
from keyboards import sex_keyboard, back_keyboard
from states import GET_SEX, EDIT_AGE, PROFILE
from handlers.profile import get_my_profile_info
from db import get_user, update_user_field
from services.age_validation import validate_age


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    valid, result = validate_age(text)

    if not valid:
        await update.message.reply_text(result)
        return  

    context.user_data['age'] = result

    await update.message.reply_text(
        'Выберите пол:',
        reply_markup=sex_keyboard()
    )

    return GET_SEX

async def edit_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        'Введите новый возраст',
        reply_markup=back_keyboard()
    )

    return EDIT_AGE


async def update_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    valid, result = validate_age(text)

    if not valid:
        await update.message.reply_text(result)
        return EDIT_AGE

    context.user_data['age'] = result

    await update_user_field(
        update.effective_user.id,
        'age',
        result
    )

    user = await get_user(update.effective_user.id)

    await get_my_profile_info(user, update.effective_message)

    return PROFILE
