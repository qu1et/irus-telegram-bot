import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

FIRST_MESSAGE, GET_ANSWER, GET_NAME, GET_NUMBER, GET_EMAIL, GET_AGREEMENT = (
    range(6)
)
AGREEMENT_TEXT = (
    "Для отправки вам данных по интересующим компаниям, нам необходимо "
    "подтверждение на обработку данных. Мы не передаем их третьим лицам. "
    'Если вас устраивает, напишите "Согласен".'
)
FEATURES_TEXT = (
    "Что вы можете получить от этого бота:\n"
    "  - Финансовые показатели компании\n"
    "  - Оценка через мультипликаторы\n"
    "  - Операционная деятельность компании\n"
    "  - Дивидендная политика. В том числе получение уведомлений об утвержденных выплатах по интересующим вас компаниям\n"
    "  - Мониторинг цены акций и получение уведомление по достижению нужной вам цены\n"
    "  - Отслеживание большой волны покупок/продаж в бумаге\n"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Приветствую, {update.effective_user.first_name}! Хотите получать аналитику по бумагам московской биржи?",
    )
    return FIRST_MESSAGE


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.effective_message.text
    if answer.strip().lower() == "да":
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Как я могу обращаться к вам?",
        )
        return GET_NAME
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Буду ждать вас, если измените решение",
        )
        return FIRST_MESSAGE


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"{name}, чтобы получать актуальную иформацию укажите ваш номер телефона:",
    )
    return GET_NUMBER


async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id, text="Введите ваш email:"
    )
    return GET_EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id, text=AGREEMENT_TEXT
    )
    return GET_AGREEMENT


async def get_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    if message.strip().lower() == "согласен":
        await context.bot.send_message(
            chat_id=update.effective_user.id, text=FEATURES_TEXT
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="К сожалению, тогда мы не можем предоставить вам функционал",
        )
        return FIRST_MESSAGE


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

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
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_number,
                )
            ],
            GET_EMAIL: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_email
                )
            ],
            GET_AGREEMENT: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND,
                    callback=get_agreement,
                )
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
