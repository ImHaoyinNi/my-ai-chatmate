import base64
import io
import os
from asyncio import sleep
from random import random

from dotenv import load_dotenv
from telegram import Update, File
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

from src.service.behavior.behavior_tree import push_message
from src.service.message_processor import message_processor_async
from src.service.message_processor.message_processor_async import MessageProcessorAsync
from src.service.message_processor.Message import MessageType, Message, message_queue
from src.service.message_processor.message_processor import MessageProcessor
from src.utils.config import config
from src.utils.logger import logger
from src.utils.utils import split_message_randomly, time_to_type, send_message


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
        res = MessageProcessorAsync.process_command(user_id, command)
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
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        text = update.message.text
        message = await MessageProcessorAsync.process_text(user_id, text)
        # await send_message(context.bot, message, user_id)

    @staticmethod
    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        voice = update.message.voice
        voice_file: File = await voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        voice_buffer = io.BytesIO(voice_bytes)
        voice_buffer.name = "voice.ogg"
        reply = await MessageProcessorAsync.process_voice(user_id, voice_buffer)
        await TelegramBot.send_message(context.bot, user_id, reply)

    @staticmethod
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.chat_id
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        image_file = await update.message.photo[-1].get_file()
        image_bytes = await image_file.download_as_bytearray()
        image_bytes = io.BytesIO(image_bytes)
        image_bytes.seek(0)
        image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
        reply = await MessageProcessorAsync.process_image(user_id, image_base64)
        await TelegramBot.send_message(context.bot, user_id, reply)

    @staticmethod
    async def set_job(update: Update, context: CallbackContext) -> None:
        interval = config.cronjob_settings['interval']
        context.job_queue.run_repeating(push_message, interval=interval, first=0)

    @staticmethod
    async def send_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
        for user_id in message_queue.queue.keys():
            while message_queue.get_length(user_id) > 0:
                message = message_queue.dequeue(user_id)
                await send_message(context.bot, user_id, message)
                logger.info(f"Sent a {message.message_type.value} message to {user_id}")

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
