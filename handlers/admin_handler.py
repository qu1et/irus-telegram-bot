import csv
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)
from config.states import (
    ADMIN_PANEL,
    CONFIRM_MESSAGE,
    SPAM_MESSAGE,
)
from db.user_crud import get_users
from logs.logger import logger


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Спислк пользователей", callback_data="users_list")],
        [
            InlineKeyboardButton(
                "Список пользователей с тегом Горячий", callback_data="hot_users_list"
            )
        ],
        [
            InlineKeyboardButton(
                "Список пользователей с тегом Обычный",
                callback_data="common_users_list",
            )
        ],
        [
            InlineKeyboardButton(
                "Список пользователей с тегом Холодный", callback_data="cold_users_list"
            )
        ],
        [
            InlineKeyboardButton(
                "Список пользователей csv", callback_data="csv_users_list"
            )
        ],
        [
            InlineKeyboardButton(
                "Получить статистику по пользователям", callback_data="get_stat"
            )
        ],
        [InlineKeyboardButton("Сделать рассылку", callback_data="send_message")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Приветствую, {update.effective_user.first_name}!",
        reply_markup=markup,
    )
    return ADMIN_PANEL


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_users()
    text = "Список всех пользователей:\n"
    text += "№ \- Username \- Имя \- Телефон \- Email\n"
    for i, user in enumerate(users, 1):
        text += f"{i}\. @{user[2]} \- {user[3]} \- {user[4]} \- {user[5]}\n"
    await context.bot.send_message(
        chat_id=update.effective_user.id, text=text, parse_mode="MarkdownV2"
    )
    await admin_start(update, context)


async def get_csv_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_users()
    with open("users.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["№", "Username", "Имя", "Телефон", "Email"])
        for i, user in enumerate(users, 1):
            writer.writerow([i, user[2], user[3], user[4], user[5]])

    await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=open("users.csv", "rb"),
        caption="Список пользователей",
    )
    await admin_start(update, context)

async def get_spam_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Напишите, что отправить в рассылке:"
    )
    return CONFIRM_MESSAGE

async def confirm_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    context.user_data["spam_message"] = message
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="yes")],
        [InlineKeyboardButton("Нет", callback_data="no")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Ваше сообщение будет выглядеть следующим образом. Начать рассылку?"
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=message,
        reply_markup=markup,
    )
    return SPAM_MESSAGE


async def spam_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_users()
    logger.info(f'Рассылка на {len(users)} пользователей началась 🚀')
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user[1],
                text=context.user_data["spam_message"],
            )
            await asyncio.sleep(0.07)
        except Exception as e:
            logger.error(f'Ошибка при отправке сообщения пользователю {user[2]}: {e} ⛔')
            continue
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Рассылка завершена',
    )
    logger.info("Рассылка завершена ✅")
    await admin_start(update, context)