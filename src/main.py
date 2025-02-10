from src.service.telegram_bot import TelegramBot
from src.utils.config import config


def main():
    bot = TelegramBot(config.telegram_bot_token)
    bot.start()


if __name__ == '__main__':
    main()