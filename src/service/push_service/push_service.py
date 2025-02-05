from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.service.ai_service import aiService
from src.service.user_session import UserSessionManager, UserSession


class PushService:
    def __init__(self, app):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        # self._setup_jobs()

    def _setup_jobs(self):
        self.scheduler.add_job(
            self.push_morning_messages,
            'cron',
            hour=00,
            minute=15,
            timezone=pytz.timezone('America/Chicago')
        )

        self.scheduler.add_job(
            self.push_random_updates,
            IntervalTrigger(seconds=30, jitter=300)  # 5分钟随机抖动
        )

    async def push_morning_messages(self):
        users = UserSessionManager.get_all_sessions()
        for user_session in users:
            if user_session.enable_push:
                try:
                    message = aiService.generate_greetings(user_session)
                    await self.app.bot.send_message(
                        chat_id=user_session.user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    print(f"[Push Error] {user_session.user_id}: {str(e)}")
                    await self.handle_push_failure(user_session, "Error: " + str(e))

    async def push_random_updates(self):
        idle_users = UserSessionManager.get_idle_user_session(hours=6)
        for user_session in idle_users:
            try:
                prompt = f"Hi Babe! How u doing?"
                message = aiService.generate_reply(user_session, prompt)
                await self.app.bot.send_message(
                    chat_id=user_session.user_id,
                    text=message,
                    reply_markup=self._create_quick_reply()
                )
            except Exception as e:
                print(f"[Push Error] {user_session.user_id}: {str(e)}")
                await self.handle_push_failure(user_session, "Error: " + str(e))

    def _create_quick_reply(self):
        """创建快速回复键盘"""
        keyboard = [
            [InlineKeyboardButton("😍 好有趣", callback_data="push_fb_good")],
            [InlineKeyboardButton("😴 晚点聊", callback_data="push_fb_busy")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def handle_push_failure(self, user_session: UserSession, message: str):
        await self.app.bot.send_message(
                    chat_id=user_session.user_id,
                    text=message,
                    parse_mode='Markdown'
                )
        user_session.enable_push = False

    async def start(self):
        self._setup_jobs()
        self.scheduler.start()
        print("Push service started")


if __name__ == '__main__':
    token = "7527442821:AAEgPRApqPuowTSB_VMRmfBBI1F4BYOCcQg"

