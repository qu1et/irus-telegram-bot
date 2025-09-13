import logging
import os
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

(
    FIRST_MESSAGE,
    GET_ANSWER,
    GET_NAME,
    GET_NUMBER,
    GET_EMAIL,
    GET_AGREEMENT,
    INLINE_BUTTON,
) = range(7)
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
    keyboard = [["Да", "Нет"]]
    markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="Желаете присоединиться к нам?",
        resize_keyboard=True,
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Приветствую, {update.effective_user.first_name}! Хотите получать аналитику по бумагам московской биржи?",
        reply_markup=markup,
    )
    return FIRST_MESSAGE


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.effective_message.text
    context.user_data["answer"] = answer
    keyboard = [[update.effective_user.first_name]]
    markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите на кнопку или введите другое имя:",
        resize_keyboard=True,
    )
    if answer.strip().lower() == "да":
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Как я могу обращаться к вам?",
            reply_markup=markup,
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
    context.user_data["name"] = name
    keyboard = [[KeyboardButton("Отправьте номер телефона", request_contact=True)]]
    markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите на кнопку",
        resize_keyboard=True,
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"{name}, чтобы получать актуальную иформацию укажите ваш номер телефона:",
        reply_markup=markup,
    )
    return GET_NUMBER


async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone_number"] = update.effective_message.contact.phone_number
    await context.bot.send_message(
        chat_id=update.effective_user.id, text="Введите ваш email:"
    )
    return GET_EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.effective_message.text
    keyboard = [["Согласен", "Не согласен"]]
    markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="Подтвердите согласие на обработку данных:",
        resize_keyboard=True,
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id, text=AGREEMENT_TEXT, reply_markup=markup
    )
    return GET_AGREEMENT


async def get_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    context.user_data["agreement"] = message
    keyboard = [
        [
            InlineKeyboardButton(
                "Базовый",
                callback_data="basic",
            ),
            InlineKeyboardButton(
                "Расширенный",
                callback_data="extended",
            ),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if message.strip().lower() == "согласен":
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Выберите план",
            reply_markup=markup,
        )
        await context.bot.send_message(
            chat_id=os.getenv("ADMIN_ID"), text=f"{context.user_data}"
        )
        return INLINE_BUTTON
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="К сожалению, тогда мы не можем предоставить вам функционал",
        )
        return FIRST_MESSAGE


async def get_leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "basic":
        keyboard = [
            [
                InlineKeyboardButton("Получить", callback_data="get"),
                InlineKeyboardButton("Не интересует", callback_data="no"),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Получите [базовый](https://parents-chew-q3e.craft.me/2PpY6OcIw0T5C4) план уже сейчас",
            reply_markup=markup,
            parse_mode="MarkdownV2",
        )
    elif query.data == "extended":
        keyboard = [
            [
                InlineKeyboardButton("Получить", callback_data="get"),
                InlineKeyboardButton("Не интересует", callback_data="no"),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Получите [расширенный](https://parents-chew-q3e.craft.me/S1Jj4dwYTEthRE) план уже сейчас",
            reply_markup=markup,
            parse_mode="MarkdownV2",
        )


async def get_lead_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    if query.data == "get":
        await query.edit_message_text(text="Спасибо за ваш выбор")
    elif query.data == "no":
        await query.edit_message_text(
            text="Нам очень жаль. Будем рады видеть вас снова!"
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
                CallbackQueryHandler(callback=get_lead_answer, pattern="^(get|no)"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
