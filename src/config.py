import json
import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        self.nvidia_api_settings: dict = {}
        self.behavior_settings: dict = {}
        self.nvidia_api_key: str = ""
        self.telegram_bot_token: str = ""
        self.aws_access_key_id: str = ""
        self.aws_secret_access_key: str = ""
        self.env: str = ""
        self.default_persona: str = ""

    def load_config(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(BASE_DIR, "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.nvidia_api_settings = config['nvidia_api_settings']
            self.behavior_settings = config['behavior_settings']
            self.default_persona = config['default_persona']

    def load_env(self):
        load_dotenv()
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.env = os.getenv("ENV")

config = Config()
config.load_config()
config.load_env()

if __name__ == '__main__':
    print(config.nvidia_api_settings)
    print(config.behavior_settings)