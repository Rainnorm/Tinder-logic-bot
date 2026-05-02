from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)
from telegram import Bot
from states import (
    MAIN_MENU,
    CHOOSE,
    GET_NAME,
    GET_AGE,
    GET_SEX,
    GET_CITY,
    GET_PHOTO,
    GET_ABOUT,
    PROFILE,
    EDIT_PROFILE,
    EDIT_NAME,
    EDIT_AGE,
    EDIT_SEX,
    EDIT_CITY,
    EDIT_PHOTO,
    EDIT_ABOUT,
    SWIPE_MODE,
    SELECT_SEX_FILTER,
    GET_SEARCH_SEX,
    EDIT_SEARCH_SEX,
    LIKES_QUEUE
    )
from dotenv import load_dotenv
import os
from handlers.start import start
from handlers.cancel import cancel, back
from handlers.profile import get_profile, edit_profile, delete_profile
from handlers.search import start_search
from handlers.register import register
from handlers.choose import choose, accept_delete
from handlers.name import get_name, edit_name, update_name
from handlers.age import get_age, edit_age, update_age
from handlers.sex import get_sex, edit_sex, update_sex
from handlers.city import get_city, edit_city, update_city
from handlers.skip import skip_photo, skip_about
from handlers.photo import get_photo, edit_photo, update_photo, delete_photo
from handlers.about import get_about, edit_about, update_about, delete_about
from db import init_db
from handlers.swipe import like, skip, like_back, start_likes_queue, skip_like
from handlers.search_sex import get_search_sex, update_search_sex, edit_search_sex
import handlers.swipe as swipe 

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
BOT = Bot(token=TOKEN)
swipe.BOT = BOT
async def on_startup(app):
    await init_db()


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],                              #Добавить автообновление username при /start а лучше не только
        states={
            MAIN_MENU: [CallbackQueryHandler(register, pattern='register'),
                        CallbackQueryHandler(start_search, pattern='search'),
                        CallbackQueryHandler(get_profile, pattern='profile'),
                        CallbackQueryHandler(start_likes_queue, pattern="^show_likes$")],

            CHOOSE: [CallbackQueryHandler(choose, pattern='yes'),
                     CallbackQueryHandler(choose, pattern='no'),
                     CallbackQueryHandler(accept_delete, pattern='delete'),
                     CallbackQueryHandler(accept_delete, pattern='no')],
            
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
                       CallbackQueryHandler(cancel, pattern='cancel')],

            GET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age),
                      CallbackQueryHandler(cancel, pattern='cancel')],

            GET_SEX: [CallbackQueryHandler(get_sex, pattern='male'),
                      CallbackQueryHandler(get_sex, pattern='female'),
                      CallbackQueryHandler(cancel, pattern='cancel')],
            
            GET_SEARCH_SEX: [CallbackQueryHandler(get_search_sex, pattern='^sex_'),
                             CallbackQueryHandler(cancel, pattern='cancel')],

            GET_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city),
                       CallbackQueryHandler(cancel, pattern='cancel')],
            
            GET_PHOTO: [MessageHandler(filters.PHOTO, get_photo),
                        CallbackQueryHandler(skip_photo, pattern='skip')],

            GET_ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_about),
                        CallbackQueryHandler(skip_about, pattern='skip')],

            PROFILE: [CallbackQueryHandler(edit_profile, pattern='edit_profile'),
                      CallbackQueryHandler(delete_profile, pattern='delete_profile'),
                      CallbackQueryHandler(cancel, pattern='cancel')],

            EDIT_PROFILE: [CallbackQueryHandler(edit_name, pattern='edit_name'),
                           CallbackQueryHandler(edit_age, pattern='edit_age'),
                           CallbackQueryHandler(edit_sex, pattern='edit_sex'),
                           CallbackQueryHandler(edit_city, pattern='edit_city'),
                           CallbackQueryHandler(edit_photo, pattern='edit_photo'),
                           CallbackQueryHandler(edit_about, pattern='edit_about'),
                           CallbackQueryHandler(edit_search_sex, pattern='edit_search_sex'),
                           CallbackQueryHandler(delete_photo, pattern='delete_photo'),
                           CallbackQueryHandler(delete_about, pattern='delete_about'),
                           CallbackQueryHandler(back, pattern='back')],
            
            EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_name),
                        CallbackQueryHandler(cancel, pattern='cancel')],
            
            EDIT_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_age),
                       CallbackQueryHandler(cancel, pattern='cancel')],

            EDIT_SEX: [CallbackQueryHandler(update_sex, pattern='male'),
                       CallbackQueryHandler(update_sex, pattern='female'),
                       CallbackQueryHandler(cancel, pattern='cancel')],

            EDIT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_city),
                        CallbackQueryHandler(cancel, pattern='cancel')],

            EDIT_PHOTO: [MessageHandler(filters.PHOTO, update_photo),
                         CallbackQueryHandler(cancel, pattern='cancel')],
            
            EDIT_ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_about),
                         CallbackQueryHandler(cancel, pattern='cancel')],
            
            EDIT_SEARCH_SEX: [CallbackQueryHandler(update_search_sex, pattern='^sex_'),
                              CallbackQueryHandler(cancel, pattern='cancel')],
            
            # SELECT_SEX_FILTER: [CallbackQueryHandler(set_search_filter),
            #                     CallbackQueryHandler(cancel, pattern='cancel')
            #                     ],

            SWIPE_MODE: [CallbackQueryHandler(like, pattern="^like_"),
                         CallbackQueryHandler(skip, pattern="^skip_"),
                         CallbackQueryHandler(cancel, pattern='cancel')],
            
            LIKES_QUEUE: [CallbackQueryHandler(like_back, pattern="^like_back_"),
                          CallbackQueryHandler(start_likes_queue, pattern="^show_likes")]
            
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(CallbackQueryHandler(skip_like, pattern="^skip_like$"))
    app.add_handler(CallbackQueryHandler(like_back, pattern=r"^like_back_"))
    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == '__main__':
    main()
