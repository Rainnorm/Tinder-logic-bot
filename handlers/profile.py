from telegram import Update
from telegram.ext import ContextTypes
from keyboards import profile_main_keyboard, start_keyboard, profile_edit_keyboard, confirm_delete_keyboard
from states import PROFILE, MAIN_MENU, EDIT_PROFILE, CHOOSE
from db import get_user
from telegram.error import BadRequest


async def get_my_profile_info(user, target, edit_flag=False):
    # user теперь словарь
    name = user.get('name', 'Не указано')
    age = user.get('age', 'Не указано')
    sex = user.get('sex', 'Не указано')
    city = user.get('city', 'Не указано')
    looking_for = user.get('looking_for', 'Не указано')
    about = user.get('about')
    photo = user.get('photo')
    # username не используется в тексте, но если нужен — user.get('username')

    text = (
        f"Вот твои данные\n\n"
        f"ИМЯ: {name}\n"
        f"ВОЗРАСТ: {age}\n"
        f"ПОЛ: {sex}\n"
        f"ГОРОД: {city}\n"
        f"ПОИСК: {looking_for}"
    )

    if about:
        text += f"\nО ТЕБЕ: {about}"

    if edit_flag:
        text += "\n\nЧто ты хочешь изменить?"

    keyboard = profile_edit_keyboard() if edit_flag else profile_main_keyboard()

    if photo:
        try:
            await target.reply_photo(
                photo=photo,
                caption=text,
                reply_markup=keyboard
            )
        except Exception:
            # fallback, если file_id повреждён
            await target.reply_text(text, reply_markup=keyboard)
    else:
        await target.reply_text(text, reply_markup=keyboard)
                 


async def get_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = await get_user(update.effective_user.id)
    
    if not user:
        try:
            await query.edit_message_text('Вы еще не зарегистроированы', reply_markup=start_keyboard())
            return MAIN_MENU
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                raise
    else:
        await get_my_profile_info(user, query.message)
        return PROFILE
    

async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await get_user(update.effective_user.id)
    edit_flag = 1
    await get_my_profile_info(user, query.message, edit_flag)
    return EDIT_PROFILE

async def delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Удалить анкету?",
        reply_markup=confirm_delete_keyboard()
    )
    return CHOOSE
    
    

