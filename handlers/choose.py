from telegram import Update
from telegram.ext import ContextTypes
from keyboards import back_keyboard, start_keyboard
from states import GET_NAME, MAIN_MENU, PROFILE
from db import delete_profile, get_user
from handlers.profile import get_my_profile_info


async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'yes':
        await delete_profile(update.effective_user.id)
        await query.edit_message_text(
            'Введите ваше имя',
            reply_markup=back_keyboard()
        )
        return GET_NAME
    else:
        await query.edit_message_text(
            'Добро пожаловать!\nВыберите действие:',
            reply_markup=start_keyboard()
        )
        return MAIN_MENU
    


async def accept_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await get_user(update.effective_user.id)
    if query.data == 'delete':
        await delete_profile(update.effective_user.id)
        await query.edit_message_text(
            'Анкета удалена',
            reply_markup=start_keyboard()
        )
        return MAIN_MENU
    else:
        await get_my_profile_info(user, query.message)
        return PROFILE