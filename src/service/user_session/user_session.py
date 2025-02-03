from src.service.type.constants import new_message, Role
from src.service.user_session.personality import Personality, get_personality_prompt


class UserSession:
    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self._reply_with_voice: bool = False
        self._max_context: int = 20

        self.personality: str = Personality.DEFAULT.value
        self.system_message: object = new_message(Role.SYSTEM, "")
        self.context: list[object] = [self.system_message]

    def add_user_context(self, user_input: str):
        self.context.append(new_message(Role.USER, user_input))
        if len(self.context) > self._max_context:
            self.context.pop(1)

    def add_bot_context(self, bot_input):
        self.context.append(new_message(Role.ASSISTANT, bot_input))
        if len(self.context) > self._max_context:
            self.context.pop(1)

    def set_personality(self, personality: str):
        personality_prompt = get_personality_prompt(personality)
        self.system_message = new_message(Role.SYSTEM, personality_prompt)
        self.personality = personality
        self.clear_context()

    def get_context(self):
        return self.context

    def clear_context(self):
        self.context.clear()
        self.context.append(self.system_message)

    @property
    def reply_with_voice(self):
        return self._reply_with_voice

    @reply_with_voice.setter
    def reply_with_voice(self, value):
        self._reply_with_voice = value


class UserSessionManager:
    sessions = {}

    @staticmethod
    def get_session(user_id) -> UserSession:
        if user_id not in UserSessionManager.sessions:
            UserSessionManager.sessions[user_id] = UserSession(user_id)
        return UserSessionManager.sessions[user_id]


if __name__ == '__main__':
    m = new_message(Role.SYSTEM, "")
    print(type(m))