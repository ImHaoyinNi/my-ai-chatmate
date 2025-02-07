import os

from dotenv import load_dotenv

from src.telegram_bot import TelegramBot


def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = TelegramBot(token)
    bot.start()


if __name__ == '__main__':
    main()