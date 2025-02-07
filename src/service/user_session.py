import time

from src.constants import new_message, Role
from src.config import config
from src.service.persona import get_persona_prompt


class UserSession:
    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self._reply_with_voice: bool = False
        self._enable_push: bool = True
        self._last_active: float = -1
        self._max_context: int = 20

        self.system_message: dict = new_message(Role.SYSTEM, "")
        self.context: list[dict] = [self.system_message]
        self.persona = config.default_persona
        self.set_persona(self.persona)

    def add_user_context(self, user_input: str):
        self.context.append(new_message(Role.USER, user_input))
        self._last_active = time.time()
        if len(self.context) > self._max_context:
            self.context.pop(1)

    def add_bot_context(self, bot_input):
        self.context.append(new_message(Role.ASSISTANT, bot_input))
        if len(self.context) > self._max_context:
            self.context.pop(1)

    def set_persona(self, persona: str):
        prompt = get_persona_prompt(persona)
        self.system_message = new_message(Role.SYSTEM, prompt)
        self.persona = persona
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
    def last_active(self):
        return self._last_active


class UserSessionManager:
    sessions = {}

    @staticmethod
    def get_session(user_id) -> UserSession:
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

if __name__ == '__main__':
    m = new_message(Role.SYSTEM, "")
    print(type(m))