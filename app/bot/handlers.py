from telegram import Update
from telegram.ext import ContextTypes
from app.bot.keyboards import inline_keyboard
from app.db.crud import add_message, add_user, can_send_message
from app.db.database import get_db
from app.db.models import User
from sqlalchemy.future import select
import asyncpg
import os


group_id = os.getenv("GROUP_ID")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat and update.message.chat.type == 'private':
        user_message = update.message.text.lower()
        user_id = update.message.from_user.id

        # Проверяем, может ли пользователь отправить сообщение (антиспам)
        if not await can_send_message(user_id):
            await update.message.reply_text('Пожалуйста, подождите 10 секунд перед отправкой следующего сообщения.')
            return

        # Получаем сессию базы данных
        async with get_db() as session:
            message = await context.bot.send_message(
                chat_id=group_id,
                text=f"{user_message}",
                reply_markup=inline_keyboard('text')
            )

            # Добавляем сообщение
            await add_message(
                session=session,
                message_id=message.message_id,
                text=user_message,
                author_id=user_id
            )


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat and update.message.chat.type == 'private':
        photo = update.message.photo[-1].file_id  # Берем фото самого высокого качества
        user_id = update.message.from_user.id

        # Получаем сессию базы данных
        async with get_db() as session:
            message = await context.bot.send_photo(
                chat_id=group_id,
                photo=photo,
                caption="Смотрите что нашел!",
                reply_markup=inline_keyboard('photo'),
                has_spoiler=True  # Устанавливаем фото как спойлер
            )

            # Добавляем сообщение
            await add_message(
                session=session,
                message_id=message.message_id,
                text=f"Фото : {photo}",
                author_id=user_id
            )
