from telegram.ext import CallbackContext, ContextTypes

from src.service.ai_service import aiService
from src.service.user_session import UserSessionManager


async def job_task(context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=context.job.chat_id, text="Reminder: Your job is running!")

async def send_random_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    idle_users = UserSessionManager.get_idle_user_session(hours=1, minutes=0)
    for user_session in idle_users:
        try:
            if user_session.enable_push:
                prompt = f"Hi Babe! How u doing?"
                message = aiService.generate_response(user_session, prompt)
                await context.bot.send_message(chat_id=user_session.user_id, text=message)
        except Exception as e:
            print(f"Error [random_message] {user_session.user_id}: {str(e)}")

