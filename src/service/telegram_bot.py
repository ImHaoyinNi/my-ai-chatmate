import base64
import io
import os

from dotenv import load_dotenv
from telegram import Update, File
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

from src.service.behavior.behavior_tree import push_message
from src.service.message_processor.Message import chat_message_store
from src.service.message_processor.user_message_processor import UserMessageProcessor
from src.service.user_session import UserSessionManager
from src.utils.config import config
from src.utils.logger import logger
from src.utils.utils import send_message


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.register_handlers()

    @staticmethod
    async def handle_command(update: Update, context: CallbackContext):
        TelegramBot.register_user(update)
        user_id = update.message.chat_id
        command = update.message.text
        if command.startswith('/'):
            command = command[1:]
        res = UserMessageProcessor.process_command(user_id, command)
        await context.bot.send_message(chat_id=user_id, text=res)

    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramBot.register_user(update)
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        text = update.message.text
        await UserMessageProcessor.process_text(user_id, text)

    @staticmethod
    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramBot.register_user(update)
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        voice = update.message.voice
        voice_file: File = await voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        voice_buffer = io.BytesIO(voice_bytes)
        voice_buffer.name = "voice.ogg"
        await UserMessageProcessor.process_voice(user_id, voice_buffer)

    @staticmethod
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramBot.register_user(update)
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        image_file = await update.message.photo[-1].get_file()
        image_bytes = await image_file.download_as_bytearray()
        image_bytes = io.BytesIO(image_bytes)
        image_bytes.seek(0)
        image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
        await UserMessageProcessor.process_image(user_id, image_base64)

    @staticmethod
    async def set_job(update: Update, context: CallbackContext) -> None:
        interval = config.cronjob_settings['interval']
        context.job_queue.run_repeating(push_message, interval=interval, first=0)

    @staticmethod
    async def send_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
        for user_id in UserSessionManager.get_all_user_id():
            while chat_message_store.get_length(user_id) > 0:
                message = chat_message_store.dequeue(user_id)
                await send_message(context.bot, user_id, message)
                logger.info(f"Sent a {message.message_type.value} message to {user_id}")

    @staticmethod
    def register_user(update: Update):
        user_id = update.message.chat_id
        user_full_name = update.message.from_user.full_name
        user_session = UserSessionManager.get_session(user_id)
        if user_session.full_name != user_full_name:
            user_session.full_name = user_full_name

    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", TelegramBot.set_job))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramBot.handle_text, block=False))
        self.app.add_handler(MessageHandler(filters.VOICE, TelegramBot.handle_voice, block=False))
        self.app.add_handler(MessageHandler(filters.PHOTO, TelegramBot.handle_photo, block=False))
        self.app.add_handler(MessageHandler(filters.COMMAND, TelegramBot.handle_command, block=False))
        logger.info("Registering handlers finished")

    def start(self):
        logger.info("Starting telegram bot")
        job_queue = self.app.job_queue
        interval = config.cronjob_settings['interval']
        job_queue.run_repeating(push_message, interval=interval, first=0)
        job_queue.run_repeating(TelegramBot.send_messages, interval=3, first=0)
        self.app.run_polling()

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = TelegramBot(token)
    bot.start()
