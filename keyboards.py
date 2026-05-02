from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard():
    keyboard = [
        [InlineKeyboardButton('Создать новую анкету', callback_data='register')],
        [InlineKeyboardButton('Начать поиск', callback_data='search'),
         InlineKeyboardButton('Профиль', callback_data='profile')],
        [InlineKeyboardButton("❤️ Кто лайкнул меня", callback_data="show_likes")]
    ]
    return InlineKeyboardMarkup(keyboard)


def profile_main_keyboard():
    keyboard = [
        [InlineKeyboardButton('Редактировать', callback_data='edit_profile')],
        [InlineKeyboardButton('Удалить профиль', callback_data='delete_profile')],
        [InlineKeyboardButton('Назад', callback_data='cancel')],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton('Создать новую', callback_data='yes'),
         InlineKeyboardButton('Отменеить', callback_data='no')]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_delete_keyboard():
    keyboard = [
        [InlineKeyboardButton('Удалить', callback_data='delete'),
         InlineKeyboardButton('Отменить', callback_data='no')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    keyboard = [
        [InlineKeyboardButton('Отмена', callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)


def sex_keyboard():
    keyboard = [
        [InlineKeyboardButton('Мужской', callback_data='male'),
         InlineKeyboardButton('Женский', callback_data='female')],
        [InlineKeyboardButton('Отмена', callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)


def skip_keyboard():
    keyboard = [
        [InlineKeyboardButton('Пропустить', callback_data='skip')]
    ]
    return InlineKeyboardMarkup(keyboard)


def profile_edit_keyboard():
    keyboard = [
        [InlineKeyboardButton('Имя', callback_data='edit_name'),
         InlineKeyboardButton('Возраст', callback_data='edit_age'),
         InlineKeyboardButton('Пол', callback_data='edit_sex')],
        [InlineKeyboardButton('Город', callback_data='edit_city'),
         InlineKeyboardButton('Описание', callback_data='edit_about'),
         InlineKeyboardButton('Фото', callback_data='edit_photo')],
        [InlineKeyboardButton('Пол поиска', callback_data='edit_search_sex')],
        [InlineKeyboardButton('Удалить фото', callback_data='delete_photo')],
        [InlineKeyboardButton('Удалить описание', callback_data='delete_about')],
        [InlineKeyboardButton('Назад', callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)


def sex_filter_keyboard():
    keyboard = [
        [InlineKeyboardButton('М', callback_data='sex_male'),
         InlineKeyboardButton('Ж', callback_data='sex_female')],
        [InlineKeyboardButton('Все', callback_data='sex_all')],
        [InlineKeyboardButton('Отмена', callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)

# def swipe_keyboard():
#     keyboard = [
#         [InlineKeyboardButton('+', callback_data='like'),
#          InlineKeyboardButton('-', callback_data='dislike')],
#         [InlineKeyboardButton('Отмена', callback_data='cancel')]
#     ]
#     return InlineKeyboardMarkup(keyboard)


def swipe_keyboard(profile_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❤️", callback_data=f"like_{profile_id}"),
            InlineKeyboardButton("👎", callback_data=f"skip_{profile_id}")
        ]
    ])