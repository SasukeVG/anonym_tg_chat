from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.bot.buttons import vote_button, threads_button
from app.bot.handlers import handle_text_message, handle_photo_message
from app.bot.commands import start, get_chat_info, command_select_topic, command_help
import os

bot_token = os.getenv("BOT_TOKEN")


def main() -> None:
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_chat_info", get_chat_info))
    application.add_handler(CommandHandler("select_topic", command_select_topic))  # Новая команда для выбора топика
    application.add_handler(CommandHandler("help", command_help))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))

    application.add_handler(CallbackQueryHandler(threads_button, pattern=r'^(select_thread|change_page):'))
    application.add_handler(CallbackQueryHandler(vote_button, pattern=r'^(delete_text|delete_photo|keep)'))

    application.run_polling()


if __name__ == '__main__':
    main()