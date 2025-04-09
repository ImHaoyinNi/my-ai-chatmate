import time
from datetime import datetime

import pytz

from src.data.user_info import insert_user
from src.persona.persona_manager import get_persona_prompt
from src.redis.redis_client import redis_client
from src.utils.config import config
from src.utils.constants import new_message, Role


class UserSession:
    def __init__(self, user_id: int, user_full_name: str = ""):
        self.user_id: int = user_id
        self._user_full_name: str = user_full_name
        self._reply_with_voice: bool = False
        self._enable_push: bool = config.user_session_settings["enable_push"]
        self._enable_image: bool = config.user_session_settings["enable_image"]
        self._last_active: float = -1
        self._max_context_length: int = config.user_session_settings["max_context_length"]

        self.system_message: dict = new_message(Role.SYSTEM, "")
        self.context: list[dict] = [self.system_message]
        self.persona_code = config.default_persona_code
        self.set_persona(self.persona_code)

    def to_string(self) -> str:
        houston_tz = pytz.timezone('America/Chicago')

        attributes = {k: v for k, v in self.__dict__.items() if k != "context"}

        if "_last_active" in attributes and attributes["_last_active"] > 0:
            attributes["_last_active"] = datetime.fromtimestamp(attributes["_last_active"], houston_tz).strftime(
                '%Y-%m-%d %H:%M:%S %Z')

        return "\n".join(f"{key}: {value}" for key, value in attributes.items())

    def add_user_context(self, user_input: str):
        self.context.append(new_message(Role.USER, user_input))
        self._last_active = time.time()
        if len(self.context) > self._max_context_length:
            self.context.pop(1)

    def add_bot_context(self, bot_input):
        self.context.append(new_message(Role.ASSISTANT, bot_input))
        if len(self.context) > self._max_context_length:
            self.context.pop(1)

    def set_persona(self, persona_code: str):
        prompt = get_persona_prompt(persona_code, self.full_name)
        if not prompt:
            raise ValueError(f"Invalid persona code: {persona_code}")
        self.system_message = new_message(Role.SYSTEM, prompt)
        self.persona_code = persona_code
        self.clear_context()

    def get_context(self):
        return self.context

    def clear_context(self):
        self.context.clear()
        self.context.append(self.system_message)

    def is_idle(self, hour: int, minute: int = 0) -> bool:
        idle_time = time.time() - self._last_active
        if idle_time >= minute * 60 + hour * 3600:
            return True
        else:
            return False

    @property
    def full_name(self) -> str:
        return self._user_full_name

    @full_name.setter
    def full_name(self, value: str):
        self._user_full_name = value
        self.set_persona(self.persona_code)

    @property
    def reply_with_voice(self):
        return self._reply_with_voice

    @reply_with_voice.setter
    def reply_with_voice(self, value):
        self._reply_with_voice = value

    @property
    def enable_push(self):
        return self._enable_push

    @enable_push.setter
    def enable_push(self, value):
        self._enable_push = value

    @property
    def enable_image(self):
        return self._enable_image

    @enable_image.setter
    def enable_image(self, value):
        self._enable_image = value

    @property
    def last_active(self):
        return self._last_active


class UserSessionManager:
    sessions: dict[int, UserSession] = {}

    @staticmethod
    def get_session(user_id: int) -> UserSession:
        if user_id not in UserSessionManager.sessions:
            UserSessionManager.sessions[user_id] = UserSession(user_id)
        return UserSessionManager.sessions[user_id]

    @staticmethod
    def get_all_sessions() -> list[UserSession]:
        return list(UserSessionManager.sessions.values())

    @staticmethod
    def get_idle_user_session(hours: int, minutes: int = 0) -> list[UserSession]:
        idle_sessions: list[UserSession] = []
        for user_session in UserSessionManager.sessions.values():
            if time.time() - user_session.last_active > 3600 * hours + 60 * minutes:
                idle_sessions.append(user_session)
        return idle_sessions

    @staticmethod
    def get_all_user_id() -> list[int]:
        return list(UserSessionManager.sessions.keys())

    @staticmethod
    def is_exist(user_id: int) -> bool:
        return user_id in UserSessionManager.sessions

if __name__ == '__main__':
    m = new_message(Role.SYSTEM, "")
    print(type(m))