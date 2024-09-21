from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import func
from sqlalchemy.future import select

from app.db.crud import add_user
from app.db.models import Thread
from app.db.database import get_db
from app.db.crud import get_threads_by_frequency
from app.bot.keyboards import create_pagination_keyboard


async def start_thread_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    async with get_db() as session:
        total_threads = await session.scalar(select(func.count(Thread.id)))
        total_pages = (total_threads + 4) // 5  # Рассчитываем количество страниц

        threads = await get_threads_by_frequency(session, limit=5, offset=0)
        keyboard = create_pagination_keyboard(threads, current_page=1, total_pages=total_pages)
        await update.message.reply_text("Выберите топик:", reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user

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
            chat_info = await context.bot.get_chat(chat_id)
            await update.message.reply_text(f"Chat title: {chat_info}")
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}")
    else:
        await update.message.reply_text("Please provide a chat ID as a parameter.")


async def command_select_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_thread_selection(update, context)


async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "/start - Запуск бота и вывод приветственного сообщения.\n"
        "/select_topic - Выбор топика для отправки сообщения.\n"
        "/help - Вывод этого списка команд.\n"
    )
    await update.message.reply_text(help_text)
