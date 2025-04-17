import random

from src.agent.agent_service import agent_service
from src.service.behavior.active_behaviors.base_active_behavior import BaseActiveBehavior
from src.data.Message import Message, MessageType
from src.agent.user_session import UserSession
from src.utils.config import config
from src.utils.utils import get_current_time


class Greetings(BaseActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(Greetings, self).__init__(user_session, bot, name="Greetings")
        self.good_morning_prompt = (
            "It's morning time. Say good morning to me."
        )
        self.good_morning_hour = 8
        self.good_morning_minute = random.randint(0, 20)

        self.good_night_prompt = (
            "It's sleep time. You should go to sleep. Say good night to me."
        )
        self.good_night_hour = 23
        self.good_night_minute = random.randint(0, 59)

    def to_continue(self) -> bool:
        is_idle = self.user_session.is_idle(0, config.greeting_settings["greeting_interval_minutes"])
        if not is_idle:
            return False
        hour, minute = get_current_time()
        if hour == 8 and abs(minute - self.good_morning_minute) <= 5:
            return True
        if hour == 23 and abs(minute - self.good_night_minute) <= 5:
            return True
        return False

    async def generate_message(self) -> Message:
        hour, minute = get_current_time()
        if hour == 8:
            self.good_night_minute = random.randint(0, 59)
            res = await agent_service.generate_reply(self.user_session, self.good_morning_prompt)
            return res
        if hour == self.good_night_hour:
            self.good_morning_minute = random.randint(0, 20)
            res = await agent_service.generate_reply(self.user_session, self.good_night_prompt)
            return res
        return Message(MessageType.NONE, "This is a none message", "", self.user_session.user_id)