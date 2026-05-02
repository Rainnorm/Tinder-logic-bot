from db import get_next_user, DB_NAME
from keyboards import swipe_keyboard
import aiosqlite

async def get_next_profile(user_id, filter_data):
    return await get_next_user(user_id, filter_data)


async def send_profile(update, context, user):
    user_id = update.effective_user.id
    target_id = user["id"]

    # -------------------------
    # 🔥 фиксируем просмотр (кулдаун / антиповторы)
    # -------------------------
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO views (user_id, target_id, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, target_id)
        )
        await db.commit()
    print("USER TYPE:", type(user))
    print("USER VALUE:", user)

    context.user_data["current_profile_id"] = user["id"]

    caption = (
        f"👤 {user['name']}, {user['age']}\n"
        f"📍 {user['city']}\n"
    )

    if user.get("about"):
        caption += f"\n💬 {user['about']}"

    if user.get("photo"):
        await update.effective_message.reply_photo(
            photo=user["photo"],
            caption=caption,
            reply_markup=swipe_keyboard(user["id"])
        )
    else:
        await update.effective_message.reply_text(
            caption,
            reply_markup=swipe_keyboard(user["id"])
        )


async def no_more_profiles(update):
    await update.effective_message.reply_text("😢 Никого больше нет")