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

