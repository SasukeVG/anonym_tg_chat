from telegram import Update
from telegram.ext import ContextTypes
from app.db.crud import add_user
from app.db.database import get_db


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
