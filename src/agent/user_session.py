import time
from datetime import datetime
from typing import List, Dict

import pytz

from src.agent.memory import memory
from src.persona.persona_manager import get_persona_prompt
from src.utils.config import config
from src.utils.constants import new_message, Role


class UserSession:
    def __init__(self, user_id: int, user_full_name: str = ""):
        self.user_id: int = user_id
        self._user_full_name: str = user_full_name
        self._reply_with_voice: bool = True
        self._enable_push: bool = config.user_session_settings["enable_push"]
        self._enable_image: bool = config.user_session_settings["enable_image"]
        self._enable_long_term_memory: bool = False
        self._last_active: float = -1
        self._max_context_length: int = config.user_session_settings["max_context_length"]
        self.persona_code = config.default_persona_code
        self.persona_prompt = ""
        # Order matters
        self.system_message: Dict = new_message(Role.SYSTEM, "")
        self.context: List[Dict] = [self.system_message]
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
        if self._enable_long_term_memory:
            memory.add(new_message(Role.USER, user_input), user_id=self.user_id)
        self._last_active = time.time()
        if len(self.context) > self._max_context_length:
            self.context.pop(1) # context[0] is system prompt

    def add_bot_context(self, bot_input):
        self.context.append(new_message(Role.ASSISTANT, bot_input))
        if self._enable_long_term_memory:
            memory.add(new_message(Role.ASSISTANT, bot_input), user_id=self.user_id)
        if len(self.context) > self._max_context_length:
            self.context.pop(1)

    def recall_memory(self, query: str, limit: int = 3) -> str:
        if not self._enable_long_term_memory:
            return ""
        relevant_memories = memory.search(query=query, user_id=self.user_id, limit=limit)
        memories_str = "\nYour memories:\n" + "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        self.context[0] = new_message(Role.SYSTEM, self.system_message["content"] + memories_str)
        return memories_str


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
    def enable_long_term_memory(self) -> bool:
        return self._enable_long_term_memory

    @enable_long_term_memory.setter
    def enable_long_term_memory(self, value: bool):
        self._enable_long_term_memory = value

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
    sessions: Dict[int, UserSession] = {}

    @staticmethod
    def get_session(user_id: int) -> UserSession:
        if user_id not in UserSessionManager.sessions:
            UserSessionManager.sessions[user_id] = UserSession(user_id)
        return UserSessionManager.sessions[user_id]

    @staticmethod
    def get_all_sessions() -> List[UserSession]:
        return list(UserSessionManager.sessions.values())

    @staticmethod
    def get_idle_user_session(hours: int, minutes: int = 0) -> List[UserSession]:
        idle_sessions: List[UserSession] = []
        for user_session in UserSessionManager.sessions.values():
            if time.time() - user_session.last_active > 3600 * hours + 60 * minutes:
                idle_sessions.append(user_session)
        return idle_sessions

    @staticmethod
    def get_all_user_id() -> List[int]:
        return list(UserSessionManager.sessions.keys())

    @staticmethod
    def is_exist(user_id: int) -> bool:
        return user_id in UserSessionManager.sessions

if __name__ == '__main__':
    m = new_message(Role.SYSTEM, "")
    print(type(m))