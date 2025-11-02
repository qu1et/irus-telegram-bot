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
    _i_dont_get_it,
    _wrong_format,
)
from handlers.admin_handler import (
    admin_start,
    list_users,
    get_csv_users_list,
    get_spam_text,
    confirm_message_text,
    spam_message,
    get_stat,
    get_hot_users_list,
    get_common_users_list,
    get_cold_users_list,
)
from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_NUMBER,
    GET_EMAIL,
    GET_AGREEMENT,
    GET_LEAD,
    ADMIN_PANEL,
    CONFIRM_MESSAGE,
    SPAM_MESSAGE,
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
                    filters=filters.Regex("^(Да|Нет)$") & ~filters.COMMAND,
                    callback=get_answer,
                ),
                MessageHandler(~filters.COMMAND, callback=_i_dont_get_it)
            ],
            GET_NAME: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_name,
                )
            ],
            GET_NUMBER: [
                MessageHandler(
                    filters=filters.CONTACT | filters.Regex("^[78]\d{10}$"),
                    callback=get_number,
                ),
                MessageHandler(~filters.COMMAND, callback=_wrong_format)
            ],
            GET_EMAIL: [
                MessageHandler(
                    filters=filters.Regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$") & ~filters.COMMAND,
                    callback=get_email,
                ),
                MessageHandler(~filters.COMMAND, callback=_wrong_format)
            ],
            GET_AGREEMENT: [
                MessageHandler(
                    filters=filters.Regex("^(Согласен|Не согласен)$") & ~filters.COMMAND,
                    callback=get_agreement,
                ),
                MessageHandler(~filters.COMMAND, callback=_i_dont_get_it)
            ],
            GET_LEAD: [
                CallbackQueryHandler(callback=get_leads, pattern="^(extended|basic)"),
            ],


            # Админка
            ADMIN_PANEL: [
                CallbackQueryHandler(callback=list_users, pattern="users_list"),
                CallbackQueryHandler(callback=get_hot_users_list, pattern="hot_users_list"),
                CallbackQueryHandler(callback=get_common_users_list, pattern="common_users_list"),
                CallbackQueryHandler(callback=get_cold_users_list, pattern="cold_users_list"),
                CallbackQueryHandler(callback=get_stat, pattern="get_stat"),
                CallbackQueryHandler(callback=get_csv_users_list, pattern="csv_users_list"),
                CallbackQueryHandler(callback=get_spam_text, pattern="send_message"),
            ],
            CONFIRM_MESSAGE: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=confirm_message_text,
                )
            ],
            SPAM_MESSAGE: [
                CallbackQueryHandler(callback=spam_message, pattern="yes"),
                CallbackQueryHandler(callback=admin_start, pattern="no"),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        persistent=True,
        name="conv_handler",
    )

    application.add_handler(conv_handler)
    logger.info("Bot started ✅")
    application.run_polling()
