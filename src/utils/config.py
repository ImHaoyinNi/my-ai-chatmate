import json
import os

from dotenv import load_dotenv

from src.utils.logger import logger


class Config:
    def __init__(self):
        # API
        self.nvidia_api_settings: dict = {}
        self.default_persona_code: str = ""
        self.user_session_settings: dict = {}
        self.ai_horde_api_settings: dict = {}
        self.stability_ai_api_settings: dict = {}

        # Behavior
        self.cronjob_settings: dict = {}
        self.is_awake_settings: dict = {}
        self.read_news_settings: dict = {}
        self.greeting_settings : dict = {}

        # Redis
        self.redis_settings: dict = {}

        # Env and secrets
        self.nvidia_api_key: str = ""
        self.telegram_bot_token: str = ""
        self.aws_access_key_id: str = ""
        self.aws_secret_access_key: str = ""
        self.env: str = ""
        self.gnews_api_key: str = ""
        self.openai_api_key: str = ""
        self.ai_horde_api_key: str = ""
        self.stability_ai_api_key: str = ""

    def load_config(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(BASE_DIR, "../config.json")
        if self.env != "production":
            config_path = os.path.join(BASE_DIR, "../config_dev.json")
        logger.info(f"Loading config from {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # API
            self.nvidia_api_settings = config['nvidia_api_settings']
            self.ai_horde_api_settings = config['ai_horde_api_settings']
            self.default_persona_code = config['default_persona_code']
            self.user_session_settings = config['user_session_settings']
            self.stability_ai_api_settings = config['stability_ai_api_settings']

            self.cronjob_settings = config['cronjob_settings']
            self.is_awake_settings = config['is_awake_settings']
            self.read_news_settings = config['read_news_settings']
            self.greeting_settings = config['greeting_settings']

            self.redis_settings = config['redis_settings']

    def load_env(self):
        load_dotenv()
        self.env = os.getenv("ENV")
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.gnews_api_key=os.getenv("GNEWS_API_KEY")
        self.openai_api_key=os.getenv("OPENAI_API_KEY")
        self.ai_horde_api_key=os.getenv("AIHORDE_API_KEY")
        self.stability_ai_api_key=os.getenv("STABILITY_AI_API_KEY")

        if self.env == "production":
            self.telegram_bot_token = os.getenv("PROD_BOT_TOKEN")
        else:
            self.telegram_bot_token = os.getenv("DEV_BOT_TOKEN")

config = Config()
config.load_env()
config.load_config()


if __name__ == '__main__':
    print(config.nvidia_api_settings)
    print(config.behavior_settings)