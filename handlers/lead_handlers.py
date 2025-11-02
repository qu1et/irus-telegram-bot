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
    GET_LEAD,
)
from handlers.jobs_handler import send_message_job
from datetime import timedelta
from db.user_crud import create_user, get_user, update_user
from db.tags_crud import set_tag, delete_tag, update_tag
from logs.logger import logger
from config.config import ADMIN_ID
from handlers.admin_handler import admin_start
from config.lead_magnets import lead_magnets

AGREEMENT_TEXT = (
    "Для отправки вам данных по интересующим компаниям, нам необходимо "
    "подтверждение на обработку данных. Мы не передаем их третьим лицам. "
    'Если вас устраивает, напишите "Согласен".'
)

async def _i_dont_get_it(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Я не понимаю, что вы имеете в виду",
    )
    
async def _wrong_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Неверный формат",
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == int(ADMIN_ID):
        return await admin_start(update, context)
    if not await get_user(update.effective_user.id):
        await create_user(update.effective_user.id, update.effective_user.username)
        logger.info("User has been created 📝")
        user = await get_user(update.effective_user.id)
        await set_tag(user[0], "Холодный")
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
        await update_tag(update.effective_user.id, "Обычный")
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
    if (
        message.strip().lower() == "согласен"
        or context.user_data["agreement"].strip().lower() == "согласен"
    ):
        await update_user(update.effective_user.id, "agreement", 1)
        await update_tag(update.effective_user.id, "Горячий")
        logger.info("Tag has been changed ℹ️")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"{context.user_data}")
        job = context.job_queue.run_once(
            send_message_job,
            when=timedelta(hours=1),
            data={"message": "Не забудьте выбрать план"},
            name=f"send_message_job_{update.effective_user.username}",
            chat_id=update.effective_user.id,
        )
        context.user_data["job_name"] = job.name
        return await _send_lead(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="К сожалению, тогда мы не можем предоставить вам функционал",
        )
        return FIRST_MESSAGE


async def _send_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Базовый", callback_data="basic"),
            InlineKeyboardButton("Расширенный", callback_data="extended"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Выберите план",
        reply_markup=markup,
    )
    return GET_LEAD


async def get_leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "basic":
        with open(lead_magnets["basic"]["img"], "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_user.id,
                photo=photo,
                caption=lead_magnets["basic"]["description"],
            )
    elif query.data == "extended":
        with open(lead_magnets["extended"]["img"], "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_user.id,
                photo=photo,
                caption=lead_magnets["extended"]["description"],
            )
    return await _send_lead(update, context)
