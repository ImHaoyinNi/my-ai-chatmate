import json
import os

from dotenv import load_dotenv

from src.service.logger import logger


class Config:
    def __init__(self):
        self.nvidia_api_settings: dict = {}
        self.default_persona: str = ""
        self.user_session_settings: dict = {}

        # Behavior
        self.cronjob_settings: dict = {}
        self.is_awake_settings: dict = {}
        self.read_news_settings: dict = {}

        # Env and secrets
        self.nvidia_api_key: str = ""
        self.telegram_bot_token: str = ""
        self.aws_access_key_id: str = ""
        self.aws_secret_access_key: str = ""
        self.env: str = ""
        self.gnews_api_key: str = ""

    def load_config(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(BASE_DIR, "config.json")
        logger.info(f"Loading config from {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.nvidia_api_settings = config['nvidia_api_settings']
            self.default_persona = config['default_persona']
            self.user_session_settings = config['user_session_settings']

            self.cronjob_settings = config['cronjob_settings']
            self.is_awake_settings = config['is_awake_settings']
            self.read_news_settings = config['read_news_settings']

    def load_env(self):
        load_dotenv()
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.gnews_api_key=os.getenv("GNEWS_API_KEY")
        self.env = os.getenv("ENV")

config = Config()
config.load_config()
config.load_env()

if __name__ == '__main__':
    print(config.nvidia_api_settings)
    print(config.behavior_settings)