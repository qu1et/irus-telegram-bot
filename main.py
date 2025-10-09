from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    PicklePersistence,
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
from handlers.admin_handler import (
    list_users,
    get_csv_users_list,
)
from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_NUMBER,
    GET_EMAIL,
    GET_AGREEMENT,
    INLINE_BUTTON,
    ADMIN_PANEL,
)
from db.database import create_tables
from logs.logger import logger
from config.config import TOKEN

if __name__ == "__main__":
    persistence = PicklePersistence(filepath="lead_bot")
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
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


            # Админка
            ADMIN_PANEL: [
                CallbackQueryHandler(callback=list_users, pattern="users_list"),
                # CallbackQueryHandler(callback=admin_start, pattern="hot_users_list"),
                # CallbackQueryHandler(callback=admin_start, pattern="common_users_list"),
                # CallbackQueryHandler(callback=admin_start, pattern="cold_users_list"),
                CallbackQueryHandler(callback=get_csv_users_list, pattern="csv_users_list"),
                # CallbackQueryHandler(callback=admin_start, pattern="send_message"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        persistent=True,
        name="conv_handler",
    )

    application.add_handler(conv_handler)
    logger.info("Bot started ✅")
    application.run_polling()
