import io
import os

from dotenv import load_dotenv
from telegram import Update, File
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from src.service.behavior.behavior import push_message
from src.config import config
from src.service.logger import logger
from src.service.message_processor.Message import MessageType
from src.service.message_processor.message_processor import MessageProcessor


# job_queue_started = False
#
# async def handle_command(update: Update, context: CallbackContext):
#     user_id = update.message.chat_id
#     command = update.message.text
#     if command.startswith('/'):
#         command = command[1:]
#     res = MessageProcessor.process_command(user_id, command)
#     await context.bot.send_message(chat_id=user_id, text=res)
#
#
# async def handle_text(update: Update, context: CallbackContext):
#     user_id = update.message.chat_id
#     text = update.message.text
#     response = MessageProcessor.process_text(user_id, text)
#     if type(response) == str:
#         await context.bot.send_message(chat_id=user_id, text=response)
#     elif type(response) == io.BytesIO:
#         response.seek(0)
#         await context.bot.send_voice(chat_id=user_id, voice=response)
#     else:
#         await context.bot.send_message(chat_id=user_id, text="Bad response")
#
#
# async def handle_voice(update: Update, context: CallbackContext):
#     user_id = update.message.chat_id
#     voice = update.message.voice
#     voice_file: File = await voice.get_file()
#     voice_bytes = await voice_file.download_as_bytearray()
#     voice_buffer = io.BytesIO(voice_bytes)
#     reply = MessageProcessor.process_voice(user_id, voice_buffer)
#     await update.message.reply_text(reply)
#
#
# async def handle_photo(update: Update, context: CallbackContext):
#     user_id = update.message.chat_id
#     image_file = update.message.photo[-1].get_file()
#     response = MessageProcessor.process_image(user_id, image_file)
#     await context.bot.send_message(chat_id=user_id, text=response)
#
#
# async def set_job(update: Update = None, context: CallbackContext = None) -> None:
#     context.job_queue.run_repeating(send_random_message, interval=10, first=0)
#     if update:
#         await update.message.reply_text('Job has been set! I will send a random message every 10 seconds.')


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
    async def handle_text(update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        text = update.message.text
        reply = MessageProcessor.process_text(user_id, text)
        match reply.message_type:
            case MessageType.TEXT:
                await context.bot.send_message(chat_id=user_id, text=reply.content)
            case MessageType.VOICE:
                await context.bot.send_voice(chat_id=user_id, voice=reply.content)
            case _:
                await context.bot.send_message(chat_id=user_id, text="Bad reply")

    @staticmethod
    async def handle_voice(update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        voice = update.message.voice
        voice_file: File = await voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        voice_buffer = io.BytesIO(voice_bytes)
        reply = MessageProcessor.process_voice(user_id, voice_buffer)
        await update.message.reply_text(reply)

    @staticmethod
    async def handle_photo(update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        image_file = update.message.photo[-1].get_file()
        response = MessageProcessor.process_image(user_id, image_file)
        await context.bot.send_message(chat_id=user_id, text=response)

    @staticmethod
    async def set_job(update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        context.job_queue.run_repeating(push_message, interval=10, first=0, data={"chat_id": chat_id})

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
        job_queue.run_repeating(push_message, interval=config.behavior_settings['interval'], first=0)
        self.app.run_polling()


load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = TelegramBot(token)

if __name__ == '__main__':
    bot.start()
