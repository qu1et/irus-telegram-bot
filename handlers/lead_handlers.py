from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)
from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_NUMBER,
    GET_EMAIL,
    GET_AGREEMENT,
    INLINE_BUTTON,
)
from handlers.jobs_handler import send_message_job
from datetime import timedelta
from db.user_crud import create_user, get_user, update_user
from db.tags_crud import set_tag, delete_tag
from logs.logger import logger
from config.config import ADMIN_ID
from handlers.admin_handler import admin_start

AGREEMENT_TEXT = (
    "Для отправки вам данных по интересующим компаниям, нам необходимо "
    "подтверждение на обработку данных. Мы не передаем их третьим лицам. "
    'Если вас устраивает, напишите "Согласен".'
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == int(ADMIN_ID):
        return await admin_start(update, context)
    if not await get_user(update.effective_user.id):
        await create_user(update.effective_user.id, update.effective_user.username)
        logger.info("User has been created 📝")
        user = await get_user(update.effective_user.id)
        await set_tag(user[0], 'Холодный')
        logger.info("Tag has been setted 📝")

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
    job = context.job_queue.run_once(
        send_message_job,
        when=timedelta(hours=1),
        data={
            "message": "Не забудьте завершить знакомство и воспользоваться возможностями бота"
        },
        name=f"send_message_job_{update.effective_user.username}",
        chat_id=update.effective_user.id,
    )
    context.user_data["job_name"] = job.name
    return FIRST_MESSAGE


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job_name" in context.user_data:
        for jobs in context.job_queue.get_jobs_by_name(context.user_data["job_name"]):
            jobs.schedule_removal()
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
        user = await get_user(update.effective_user.id)
        print(user[0])
        await delete_tag(user[0])
        await set_tag(user[0], 'Обычный')
        logger.info("Tag has been changed ℹ️")
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Как я могу обращаться к вам?",
            reply_markup=markup,
        )
        job = context.job_queue.run_once(
            send_message_job,
            when=timedelta(hours=1),
            data={
                "message": "Не забудьте завершить знакомство и воспользоваться возможностями бота"
            },
            name=f"send_message_job_{update.effective_user.username}",
            chat_id=update.effective_user.id,
        )
        context.user_data["job_name"] = job.name
        return GET_NAME
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Буду ждать вас, если измените решение",
        )
        return FIRST_MESSAGE


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job_name" in context.user_data:
        for jobs in context.job_queue.get_jobs_by_name(context.user_data["job_name"]):
            jobs.schedule_removal()
    name = update.effective_message.text
    await update_user(update.effective_user.id, "name", name)
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
    job = context.job_queue.run_once(
        send_message_job,
        when=timedelta(hours=1),
        data={
            "message": "Не забудьте завершить знакомство и воспользоваться возможностями бота"
        },
        name=f"send_message_job_{update.effective_user.username}",
        chat_id=update.effective_user.id,
    )
    context.user_data["job_name"] = job.name
    return GET_NUMBER


async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job_name" in context.user_data:
        for jobs in context.job_queue.get_jobs_by_name(context.user_data["job_name"]):
            jobs.schedule_removal()
    phone = update.effective_message.contact.phone_number
    await update_user(update.effective_user.id, "phone", phone)
    context.user_data["phone_number"] = phone
    await context.bot.send_message(
        chat_id=update.effective_user.id, text="Введите ваш email:"
    )
    job = context.job_queue.run_once(
        send_message_job,
        when=timedelta(hours=1),
        data={
            "message": "Не забудьте завершить знакомство и воспользоваться возможностями бота"
        },
        name=f"send_message_job_{update.effective_user.username}",
        chat_id=update.effective_user.id,
    )
    context.user_data["job_name"] = job.name
    return GET_EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job_name" in context.user_data:
        for jobs in context.job_queue.get_jobs_by_name(context.user_data["job_name"]):
            jobs.schedule_removal()
    email = update.effective_message.text
    await update_user(update.effective_user.id, "email", email)
    context.user_data["email"] = email
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
    job = context.job_queue.run_once(
        send_message_job,
        when=timedelta(hours=1),
        data={
            "message": "Не забудьте завершить знакомство и воспользоваться возможностями бота"
        },
        name=f"send_message_job_{update.effective_user.username}",
        chat_id=update.effective_user.id,
    )
    context.user_data["job_name"] = job.name
    return GET_AGREEMENT


async def get_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job_name" in context.user_data:
        for jobs in context.job_queue.get_jobs_by_name(context.user_data["job_name"]):
            jobs.schedule_removal()
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
        await update_user(update.effective_user.id, "agreement", 1)
        user = await get_user(update.effective_user.id)
        await delete_tag(user[0])
        await set_tag(user[0], 'Горячий')
        logger.info("Tag has been changed ℹ️")

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Выберите план",
            reply_markup=markup,
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"{context.user_data}")
        job = context.job_queue.run_once(
            send_message_job,
            when=timedelta(hours=1),
            data={"message": "Не забудьте выбрать план"},
            name=f"send_message_job_{update.effective_user.username}",
            chat_id=update.effective_user.id,
        )
        context.user_data["job_name"] = job.name
        return INLINE_BUTTON
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="К сожалению, тогда мы не можем предоставить вам функционал",
        )
        return FIRST_MESSAGE


async def get_leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job_name" in context.user_data:
        for jobs in context.job_queue.get_jobs_by_name(context.user_data["job_name"]):
            jobs.schedule_removal()
    query = update.callback_query
    await query.answer()
    if query.data == "basic":
        keyboard = [
            [
                InlineKeyboardButton(
                    "План", url="https://parents-chew-q3e.craft.me/2PpY6OcIw0T5C4"
                ),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Получите базовый план уже сейчас",
            reply_markup=markup,
            parse_mode="MarkdownV2",
        )
    elif query.data == "extended":
        keyboard = [
            [
                InlineKeyboardButton(
                    "План", url="https://parents-chew-q3e.craft.me/S1Jj4dwYTEthRE"
                ),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Получите расширенный план уже сейчас",
            reply_markup=markup,
            parse_mode="MarkdownV2",
        )
