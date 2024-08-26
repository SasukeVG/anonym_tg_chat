from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def inline_keyboard(message_type):
    keyboard = [
        [
            InlineKeyboardButton("👍🏻", callback_data=f'keep_{message_type}'),
            InlineKeyboardButton("👎🏻", callback_data=f'delete_{message_type}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
