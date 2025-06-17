import os
import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import inline_keyboard
from app.bot.commands import start_thread_selection
from app.db.database import get_db
from app.db.crud import (
    add_message, can_send_message, create_thread, frequency_increase,
)


logger = logging.getLogger(__name__)

group_id = os.getenv("GROUP_ID")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat and update.message.chat.type == 'private':
        user_message = update.message.text.lower()
        user_id = update.message.from_user.id

        # Проверяем, может ли пользователь отправить сообщение (антиспам)
        # if not await can_send_message(user_id):
        #     await update.message.reply_text('Пожалуйста, подождите 10 секунд перед отправкой следующего сообщения.')
        #     return

        # Проверяем, выбран ли топик
        if 'selected_thread' not in context.user_data:
            await update.message.reply_text('Пожалуйста, сначала выберите топик.')
            return

        thread_id = context.user_data['selected_thread']

        # Получаем сессию базы данных
        async with get_db() as session:
            message = await context.bot.send_message(
                chat_id=group_id,
                text=f"{user_message}",
                reply_to_message_id=thread_id if thread_id else None,
                reply_markup=inline_keyboard('text')
            )

            # Добавляем сообщение
            await add_message(
                session=session,
                message_id=message.message_id,
                text=user_message,
                author_id=user_id
            )

        await start_thread_selection(update, context)
    else:
        # Логика для обработки сообщений в группе
        if update.message.from_user.id == 324974672:
            user = update.message.from_user
            chat_id = update.message.chat_id
            thread_id = update.message.message_thread_id
            message_text = update.message.text

            log_entry = (f"User: {user.username} (ID: {user.id}),"
                         f" Chat ID: {chat_id}, Thread ID: {thread_id}, Message: {message_text}")
            logger.info(log_entry)

            # Записываем данные в базу данных
            async with get_db() as session:
                await create_thread(session, chat_id=chat_id, thread_id=thread_id, title=message_text)
        else:
            thread = update.message.message_thread_id
            chat_id = update.message.chat_id

            async with get_db() as session:
                await frequency_increase(session, thread_id=thread, chat_id=chat_id)


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat and update.message.chat.type == 'private':
        photo = update.message.photo[-1].file_id  # Берем фото самого высокого качества
        user_id = update.message.from_user.id

        # Проверяем, выбран ли топик
        if 'selected_thread' not in context.user_data:
            await update.message.reply_text('Пожалуйста, сначала выберите топик.')
            return

        thread_id = context.user_data['selected_thread']

        # Получаем сессию базы данных
        async with get_db() as session:
            message = await context.bot.send_photo(
                chat_id=group_id,
                photo=photo,
                caption="Смотрите что нашел!",
                reply_to_message_id=thread_id if thread_id else None,
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
        await start_thread_selection(update, context)