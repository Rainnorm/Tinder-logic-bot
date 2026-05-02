from telegram import Update
from telegram.ext import ContextTypes
from keyboards import confirm_keyboard, back_keyboard
from states import CHOOSE, GET_NAME
from db import get_user


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = context.application.bot_data["pool"]
    user = await get_user(pool, update.effective_user.id)
    if user:
        await query.edit_message_text(
            'У вас уже есть анкета. Создать новую с нуля?\n!Это удалит существующую анкету!',
            reply_markup=confirm_keyboard()
        )

        return CHOOSE
    
    await query.edit_message_text(
            'Введите ваше имя',
            reply_markup=back_keyboard()
        )
    return GET_NAME
