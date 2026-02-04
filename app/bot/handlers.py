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
    try:
        if update.message and update.message.chat and update.message.chat.type == 'private':
            user_message = (update.message.text or "").lower()
            user_id = update.message.from_user.id
            logger.info("handle_text_message: received private message | user_id=%s", user_id)

            # Проверяем, может ли пользователь отправить сообщение (антиспам)
            # if not await can_send_message(user_id):
            #     logger.warning("rate_limited: user_id=%s", user_id)
            #     await update.message.reply_text('Пожалуйста, подождите 10 секунд перед отправкой следующего сообщения.')
            #     return

            # Проверяем, выбран ли топик
            if 'selected_thread' not in context.user_data:
                logger.warning("selected_thread_missing: user_id=%s", user_id)
                await update.message.reply_text('Пожалуйста, сначала выберите топик.')
                return

            thread_id = context.user_data['selected_thread']
            logger.debug("forwarding_text_to_group | user_id=%s thread_id=%s", user_id, thread_id)

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

            logger.info("text_forwarded_and_saved | user_id=%s message_id=%s", user_id, message.message_id)
            await start_thread_selection(update, context)
        else:
            # Логика для обработки сообщений в группе
            if update.message.from_user.id == 324974672:
                user = update.message.from_user
                chat_id = update.message.chat_id
                thread_id = update.message.message_thread_id
                message_text = update.message.text

                log_entry = (f"admin_message | user={user.username} (id={user.id}) "
                             f"chat_id={chat_id} thread_id={thread_id}")
                logger.info(log_entry)

                # Записываем данные в базу данных
                async with get_db() as session:
                    await create_thread(session, chat_id=chat_id, thread_id=thread_id, title=message_text)
                logger.info("thread_created | chat_id=%s thread_id=%s", chat_id, thread_id)
            else:
                thread = update.message.message_thread_id
                chat_id = update.message.chat_id
                logger.debug("frequency_increase | chat_id=%s thread_id=%s", chat_id, thread)

                async with get_db() as session:
                    await frequency_increase(session, thread_id=thread, chat_id=chat_id)
                logger.info("frequency_increased | chat_id=%s thread_id=%s", chat_id, thread)
    except Exception:
        logger.exception("handle_text_message_failed")
        try:
            if update.message and update.message.chat and update.message.chat.type == 'private':
                await update.message.reply_text('Произошла ошибка при обработке сообщения. Попробуйте позже.')
        except Exception:
            # Avoid raising from logging/notification errors
            pass


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.message and update.message.chat and update.message.chat.type == 'private':
            photo = update.message.photo[-1].file_id  # Берем фото самого высокого качества
            user_id = update.message.from_user.id
            logger.info("handle_photo_message: received private photo | user_id=%s", user_id)

            # Проверяем, выбран ли топик
            if 'selected_thread' not in context.user_data:
                logger.warning("selected_thread_missing: user_id=%s", user_id)
                await update.message.reply_text('Пожалуйста, сначала выберите топик.')
                return

            thread_id = context.user_data['selected_thread']
            logger.debug("forwarding_photo_to_group | user_id=%s thread_id=%s", user_id, thread_id)

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
            logger.info("photo_forwarded_and_saved | user_id=%s message_id=%s", user_id, message.message_id)
            await start_thread_selection(update, context)
    except Exception:
        logger.exception("handle_photo_message_failed")
        try:
            if update.message and update.message.chat and update.message.chat.type == 'private':
                await update.message.reply_text('Произошла ошибка при обработке фото. Попробуйте позже.')
        except Exception:
            pass