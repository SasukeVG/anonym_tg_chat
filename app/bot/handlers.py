from telegram import Update
from telegram.ext import ContextTypes
from app.bot.keyboards import inline_keyboard
from app.db.crud import add_message
from app.db.database import get_db
import os

group_id = os.getenv("GROUP_ID")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat and update.message.chat.type == 'private':
        user_message = update.message.text
        message = await context.bot.send_message(
            chat_id=group_id,
            text=f"Анонимное сообщение:\n{user_message}",
            reply_markup=inline_keyboard('text')
        )
        # Получаем сессию базы данных
        async with get_db() as session:
            # Вызываем функцию для добавления сообщения
            await add_message(
                session=session,
                message_id=message.message_id,
                text=user_message,
                author_id=update.message.from_user.id
            )


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat and update.message.chat.type == 'private':
        photo = update.message.photo[-1].file_id  # Берем фото самого высокого качества
        message = await context.bot.send_photo(
            chat_id=group_id,
            photo=photo,
            caption="Анонимное фото",
            reply_markup=inline_keyboard('photo'),
            has_spoiler=True  # Устанавливаем фото как спойлер
        )

        # Получаем сессию базы данных
        async with get_db() as session:
            # Вызываем функцию для добавления сообщения
            await add_message(
                session=session,
                message_id=message.message_id,
                text=f"Фото : {photo}",
                author_id=update.message.from_user.id
            )
