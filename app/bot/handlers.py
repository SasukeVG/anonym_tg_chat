from telegram import Update
from telegram.ext import ContextTypes
from app.bot.keyboards import inline_keyboard
from app.db.crud import add_message, can_send_message, create_thread
from app.db.database import get_db
import os
import logging

logger = logging.getLogger(__name__)


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
    else:
        if update.message.from_user.id == 324974672:
            user = update.message.from_user
            chat_id = update.message.chat_id
            thread_id = update.message.message_thread_id
            message_text = update.message.text

            log_entry = f"User: {user.username} (ID: {user.id}), Chat ID: {chat_id}, Thread ID: {thread_id}, Message: {message_text}"
            print(log_entry)
            logger.info(log_entry)

            # Записываем данные в базу данных
            async with get_db() as session:
                await create_thread(session, chat_id=chat_id, thread_id=thread_id, title=message_text)


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
