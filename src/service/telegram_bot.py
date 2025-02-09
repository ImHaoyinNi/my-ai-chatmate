import asyncio
import base64
import io
import os

from dotenv import load_dotenv
from telegram import Update, File
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

from src.service.behavior.behavior_tree import push_message
from src.config import config
from src.service.logger import logger
from src.service.message_processor.Message import MessageType, Message
from src.service.message_processor.message_processor import MessageProcessor


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.register_handlers()

    @staticmethod
    async def handle_command(update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        command = update.message.text
        if command.startswith('/'):
            command = command[1:]
        res = MessageProcessor.process_command(user_id, command)
        await context.bot.send_message(chat_id=user_id, text=res)

    @staticmethod
    async def send_message(bot, user_id: int, message: Message):
        match message.message_type:
            case MessageType.TEXT:
                await bot.send_message(chat_id=user_id, text=message.content)
            case MessageType.VOICE:
                await bot.send_voice(chat_id=user_id, voice=message.content)
            case _:
                await bot.send_message(chat_id=user_id, text="Bad reply")

    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.chat_id
        success = await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        text = update.message.text
        message = MessageProcessor.process_text(user_id, text)
        match message.message_type:
            case MessageType.TEXT:
                await context.bot.send_message(chat_id=user_id, text=message.content)
            case MessageType.VOICE:
                await context.bot.send_voice(chat_id=user_id, voice=message.content)
            case _:
                await context.bot.send_message(chat_id=user_id, text="Bad reply")

    @staticmethod
    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        voice = update.message.voice
        voice_file: File = await voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        voice_buffer = io.BytesIO(voice_bytes)
        reply = MessageProcessor.process_voice(user_id, voice_buffer)
        await TelegramBot.send_message(context.bot, user_id, reply)

    @staticmethod
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        image_file = await update.message.photo[-1].get_file()
        image_bytes = await image_file.download_as_bytearray()
        image_bytes = io.BytesIO(image_bytes)
        image_bytes.seek(0)
        # Convert to Base64
        image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
        reply = MessageProcessor.process_image(user_id, image_base64)
        await TelegramBot.send_message(context.bot, user_id, reply)

    @staticmethod
    async def set_job(update: Update, context: CallbackContext) -> None:
        context.job_queue.run_repeating(push_message, interval=config.cronjob_settings['interval'], first=0)

    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", TelegramBot.set_job))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramBot.handle_text))
        self.app.add_handler(MessageHandler(filters.VOICE, TelegramBot.handle_voice))
        self.app.add_handler(MessageHandler(filters.PHOTO, TelegramBot.handle_photo))
        self.app.add_handler(MessageHandler(filters.COMMAND, TelegramBot.handle_command))
        logger.info("Registering handlers finished")

    def start(self):
        logger.info("Starting telegram bot")
        job_queue = self.app.job_queue
        job_queue.run_repeating(push_message, interval=config.cronjob_settings['interval'], first=0)
        self.app.run_polling()


load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = TelegramBot(token)

if __name__ == '__main__':
    bot.start()
