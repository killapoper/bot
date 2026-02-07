from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN
from handlers import *
from admin_handlers import admin_start, admin_actions
import logging
import sys

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a notice to the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # If possible, notify the user or admin
    if update and hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text("Произошла ошибка на сервере. Разработчики уже в курсе.")

def main():
    logger.info("Starting bot...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Error handler
    application.add_error_handler(error_handler)

    # Admin Handlers
    application.add_handler(CommandHandler("admin", admin_start))
    application.add_handler(CallbackQueryHandler(admin_actions, pattern="^admin_(?!menu$)")) # Exclude admin_menu if it clashes? 
    # Actually admin_actions handles `admin_download` etc.
    # `admin_menu` is for initializing the menu. `admin_start` logic handles initialization.
    application.add_handler(CallbackQueryHandler(admin_start, pattern="^admin_menu$"))

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start), 
            CommandHandler("new", start),
            CallbackQueryHandler(start, pattern="^restart$")
        ],
        states={
            INPUT_USER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_user_name)
            ],
            SELECT_TYPE: [CallbackQueryHandler(select_type)],
            INPUT_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_count),
                CallbackQueryHandler(input_count, pattern="^back$") 
            ],
            POSITION_PHOTO: [
                MessageHandler(filters.PHOTO, position_photo),
                MessageHandler(~filters.PHOTO & ~filters.COMMAND, invalid_photo_input),
                CallbackQueryHandler(position_photo, pattern="^back$")
            ],
            POSITION_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, position_name),
                CallbackQueryHandler(position_name, pattern="^back$")
            ],
            POSITION_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, position_price),
                CallbackQueryHandler(position_price, pattern="^back$")
            ],
            INPUT_ORG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_org),
                CallbackQueryHandler(input_org, pattern="^back$")
            ],
            INPUT_CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_contact),
                CallbackQueryHandler(input_contact, pattern="^back$")
            ],
            SELECT_INDUSTRY: [
                CallbackQueryHandler(select_industry)
            ],
            INPUT_RECIPIENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_recipient),
                CallbackQueryHandler(input_recipient, pattern="^back$")
            ],
            SELECT_DATE: [
                CallbackQueryHandler(select_date)
            ],
            INPUT_CUSTOM_DATE: [
                CallbackQueryHandler(input_custom_date, pattern="^back$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_custom_date)
            ],
            INPUT_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, input_receipt),
                CallbackQueryHandler(input_receipt, pattern="^back$"),
                MessageHandler(~(filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, invalid_photo_input)
            ],
            SELECT_1C: [
                CallbackQueryHandler(select_1c)
            ],
            CONFIRM_SUMMARY: [
                CallbackQueryHandler(confirm_summary)
            ],
            CONFIRM: [
                CallbackQueryHandler(confirm)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
