from src.config import config
from src.service.telegram_bot import TelegramBot


def main():
    bot = TelegramBot(config.telegram_bot_token)
    bot.start()


if __name__ == '__main__':
    main()