from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from app.db.crud import get_votes_and_text_by_message_id, update_positive_votes, update_negative_votes, has_user_voted, \
    add_vote
from app.db.database import get_db
from app.db.models import VoteType


def inline_keyboard(message_type):
    keyboard = [
        [
            InlineKeyboardButton("👍🏻", callback_data=f'keep_{message_type}'),
            InlineKeyboardButton("👎🏻", callback_data=f'delete_{message_type}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    message_id = query.message.message_id
    user_id = query.from_user.id

    async with get_db() as session:
        votes = await get_votes_and_text_by_message_id(session, message_id)
        # Проверяем, голосовал
        # ли
        # пользователь
        if await has_user_voted(session, user_id, message_id):
            await query.answer("Вы уже голосовали за это сообщение.", show_alert=True)
            return

    positive_votes = votes.get("positive_votes", 0)
    negative_votes = votes.get("negative_votes", 0)
    text_message = votes.get("text", "")

    if 'delete_text' in query.data:
        if negative_votes < 2:
            async with get_db() as session:
                if await add_vote(session, user_id, message_id, VoteType.negative):
                    await update_negative_votes(session, message_id)
                    negative_votes += 1
            t = f"Анонимное сообщение: \n{text_message} \n\n👍🏻 {positive_votes} 👎🏻 {negative_votes}"
            await query.edit_message_text(t)
            await query.edit_message_reply_markup(reply_markup=inline_keyboard('text'))
        else:
            new_text = f"Cообщение скрыто:\n||{text_message}||"
            await query.edit_message_text(text=new_text, parse_mode='MarkdownV2')

    elif 'delete_photo' in query.data:
        if negative_votes < 2:
            async with get_db() as session:
                if await add_vote(session, user_id, message_id, VoteType.negative):
                    await update_negative_votes(session, message_id)
                    negative_votes += 1
        else:
            new_text = f"Фото удалено"
            await query.edit_message_caption(caption=new_text)
            await query.edit_message_reply_markup(reply_markup=None)

    elif 'keep' in query.data:
        if positive_votes < 2:
            async with get_db() as session:
                if await add_vote(session, user_id, message_id, VoteType.positive):
                    await update_positive_votes(session, message_id)
                    positive_votes += 1
            t = f"Анонимное сообщение: \n{text_message} \n\n👍🏻 {positive_votes} 👎🏻 {negative_votes}"
            await query.edit_message_text(t)
            await query.edit_message_reply_markup(reply_markup=inline_keyboard('text'))

        else:
            # убрать кнопки и счетчики голосов
            await query.edit_message_text(text=text_message)
