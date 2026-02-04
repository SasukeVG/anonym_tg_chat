from telegram import Update
from telegram.ext import ContextTypes
import logging
from sqlalchemy import func
from sqlalchemy.future import select

from app.db.crud import add_user
from app.db.models import Thread
from app.db.database import get_db
from app.db.crud import get_threads_by_frequency
from app.bot.keyboards import create_pagination_keyboard


logger = logging.getLogger(__name__)


async def start_thread_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info("start_thread_selection | user_id=%s", user_id)
    async with get_db() as session:
        total_threads = await session.scalar(select(func.count(Thread.id)))
        total_pages = (total_threads + 4) // 5  # Рассчитываем количество страниц

        threads = await get_threads_by_frequency(session, limit=5, offset=0)
        keyboard = create_pagination_keyboard(threads, current_page=1, total_pages=total_pages)
        await update.message.reply_text("Выберите топик:", reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("command /start | user_id=%s", user.id)

    # Получаем сессию базы данных
    async with get_db() as session:
        # Вызываем функцию для добавления пользователя
        await add_user(
            session=session,
            username=user.username,
            user_id=user.id,
            name=user.first_name,
            surname=user.last_name
        )
    await update.message.reply_text('Привет! Отправь мне сообщение или фото, и я анонимно передам его в группу.')


async def get_chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем аргументы команды
    if context.args:
        chat_id = context.args[0]

        # Вызов функции get_chat
        try:
            logger.info("command /get_chat_info | chat_id=%s", chat_id)
            chat_info = await context.bot.get_chat(chat_id)
            await update.message.reply_text(f"Chat title: {chat_info}")
        except Exception as e:
            logger.exception("get_chat_info_failed | chat_id=%s", chat_id)
            await update.message.reply_text(f"An error occurred: {e}")
    else:
        await update.message.reply_text("Please provide a chat ID as a parameter.")


async def command_select_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("command /select_topic | user_id=%s", update.message.from_user.id)
    await start_thread_selection(update, context)


async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("command /help | user_id=%s", update.message.from_user.id)
    help_text = (
        "/start - Запуск бота и вывод приветственного сообщения.\n"
        "/select_topic - Выбор топика для отправки сообщения.\n"
        "/help - Вывод этого списка команд.\n"
    )
    await update.message.reply_text(help_text)
