from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.crud import get_threads_by_frequency


def inline_keyboard(message_type):
    keyboard = [
        [
            InlineKeyboardButton("👍🏻", callback_data=f'keep_{message_type}'),
            InlineKeyboardButton("👎🏻", callback_data=f'delete_{message_type}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_pagination_keyboard(threads, current_page, total_pages):
    buttons = []
    for thread in threads:
        buttons.append([InlineKeyboardButton(thread.title, callback_data=f"select_thread:{thread.thread_id}")])

    # Добавляем кнопки пагинации
    pagination_buttons = []
    if current_page > 1:
        pagination_buttons.append(InlineKeyboardButton("⏪", callback_data=f"change_page:{current_page - 1}"))
    if current_page < total_pages:
        pagination_buttons.append(InlineKeyboardButton("⏩", callback_data=f"change_page:{current_page + 1}"))

    buttons.append(pagination_buttons)
    buttons.insert(0, [InlineKeyboardButton("General", callback_data="select_thread:none")])

    return InlineKeyboardMarkup(buttons)
