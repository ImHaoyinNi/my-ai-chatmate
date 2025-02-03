import io
from telegram import Update, File
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from src.message_processor import MessageProcessor


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.register_handlers()

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Hello! I'm your bot. Send me a message!")

    async def handle_text(self, update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        text = update.message.text
        response = MessageProcessor.process_text(user_id, text)
        if type(response) == str:
            await context.bot.send_message(chat_id=user_id, text=response)
        elif type(response) == io.BytesIO:
            response.seek(0)
            await context.bot.send_voice(chat_id=user_id, voice=response)
        else:
            await context.bot.send_message(chat_id=user_id, text="Bad response")

    async def handle_voice(self, update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        voice = update.message.voice
        voice_file: File = await voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        voice_buffer = io.BytesIO(voice_bytes)
        reply = MessageProcessor.process_voice(user_id, voice_buffer)
        await update.message.reply_text(reply)

    async def handle_photo(self, update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        image_file = update.message.photo[-1].get_file()
        response = MessageProcessor.process_image(user_id, image_file)
        await context.bot.send_message(chat_id=user_id, text=response)

    async def handle_command(self, update: Update, context: CallbackContext):
        user_id = update.message.chat_id
        command = update.message.text
        if command.startswith('/'):
            command = command[1:]
        res = MessageProcessor.process_command(user_id, command)
        await context.bot.send_message(chat_id=user_id, text=res)

    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.COMMAND, self.handle_command))
        print("Start polling...")
        self.app.run_polling()


if __name__ == "__main__":
    token = "7527442821:AAEgPRApqPuowTSB_VMRmfBBI1F4BYOCcQg"
    bot = TelegramBot(token)