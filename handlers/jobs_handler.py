from telegram.ext import ContextTypes


async def send_message_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=job.data["message"])
