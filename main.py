import logging
import os
from dotenv import load_dotenv

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from handlers.lead_handlers import (
    start,
    get_answer,
    get_name,
    get_number,
    get_email,
    get_agreement,
    get_leads,
)
from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_NUMBER,
    GET_EMAIL,
    GET_AGREEMENT,
    INLINE_BUTTON,
)
from db.database import create_tables

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token(os.getenv("TOKEN"))
        .post_init(create_tables)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_MESSAGE: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_answer,
                ),
            ],
            GET_NAME: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_name,
                )
            ],
            GET_NUMBER: [
                MessageHandler(
                    filters=filters.CONTACT,
                    callback=get_number,
                )
            ],
            GET_EMAIL: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_email,
                )
            ],
            GET_AGREEMENT: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_agreement,
                )
            ],
            INLINE_BUTTON: [
                CallbackQueryHandler(callback=get_leads, pattern="^(extended|basic)"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
