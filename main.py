from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from conf.settings import TOKEN
from handlers import help_command, ask_url, process_url, ASK_URL

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).concurrent_updates(True).build()

    # Define the conversation handler for the /archive command
    archive_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("archive", lambda update, context: ask_url(update, context, 'archive'))],
        states={
            ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_url)],
        },
        fallbacks=[],
        per_user=True,  # Ensure each user's state is managed individually
    )

    # Define the conversation handler for the /extract command
    extract_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("extract", lambda update, context: ask_url(update, context, 'extract'))],
        states={
            ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_url)],
        },
        fallbacks=[],
        per_user=True,  # Ensure each user's state is managed individually
    )

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(archive_conv_handler)  # Add conversation handler for /archive command
    application.add_handler(extract_conv_handler)  # Add conversation handler for /extract command

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()