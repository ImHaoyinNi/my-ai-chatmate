import asyncio
import random
import re

import py_trees

from src.service.ai_service.ai_service_async import ai_service_async
from src.service.message_processor.Message import Message, MessageType
from src.service.user_session import UserSession
from src.utils.constants import Role
from src.utils.logger import logger
from src.utils.utils import get_current_time, send_message


class BaseActiveBehavior(py_trees.behaviour.Behaviour):
    def __init__(self, user_session: UserSession, bot, name="Base Send Message"):
        super(BaseActiveBehavior, self).__init__(name=name)
        self.user_session = user_session
        self.bot = bot
        self.logger = py_trees.logging.Logger(name=self.name)
        self._running_task = None
        self._message_generation_task = None

    def to_continue(self) -> bool:
        raise NotImplementedError

    async def generate_message(self) -> Message:
        raise NotImplementedError

    async def send_content(self, message: Message):
        await send_message(self.bot, self.user_session.user_id, message)

    def _on_message_complete(self, future):
        try:
            future.result()  # This will raise any exceptions that occurred
            logger.info(f"{self.name} message sent successfully")
        except Exception as e:
            self.logger.error(f"Error in message task: {str(e)}")

    def update(self):
        logger.info(f"Behavior update: {self.name}")
        if not self.to_continue():
            return py_trees.common.Status.FAILURE
        logger.info(f"===={self.name} was triggered====")
        try:
            loop = asyncio.get_event_loop()
            if not self._message_generation_task:
                self._message_generation_task = loop.create_task(self.generate_message())
                return py_trees.common.Status.RUNNING
            if not self._message_generation_task.done():
                return py_trees.common.Status.RUNNING

            try:
                message = self._message_generation_task.result()
            except Exception as e:
                self.logger.error(f"Error generating message: {str(e)}")
                self._message_generation_task = None
                return py_trees.common.Status.FAILURE
            self._message_generation_task = None
            if message.message_type in (MessageType.NONE, MessageType.BAD_MESSAGE):
                return py_trees.common.Status.FAILURE
            return py_trees.common.Status.SUCCESS

        except Exception as e:
            self.logger.error(f"Error in update: {str(e)}")
            return py_trees.common.Status.FAILURE

    def terminate(self, new_status):
        if self._message_generation_task and not self._message_generation_task.done():
            self._message_generation_task.cancel()
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()
        super().terminate(new_status)

# TODO: Broken
class AskingForReply(BaseActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(AskingForReply, self).__init__(user_session, bot, name="Asking For Reply")
        self.waiting_minutes: int = random.randint(3, 5)
        self.max_waiting_minutes: int = 15
        self.prompt = (
            f"You have waited for my reply for {self.waiting_minutes} minutes. "
            "But I still didn't reply your message for a while. "
            "Based on your persona, feel free to take the lead and ask for my reply."
        )

    def is_last_sentence_question(self, text: str):
        # Split sentences considering punctuation like . ! ? (Handles potential trailing spaces or emojis)
        sentences = re.split(r'(?<=[.?!])\s+', text.strip())
        # Filter out empty sentences (possible due to trailing spaces or emojis)
        sentences = [s for s in sentences if s]
        # Check if the last sentence ends with a question mark
        if sentences and sentences[-1].strip().endswith('?'):
            return True
        else:
            return False

    def to_continue(self) -> bool:
        last_message = self.user_session.context[-1]
        if last_message["role"] == Role.USER.value:
            return False
        if not self.is_last_sentence_question(last_message["content"]):
            return False
        is_idle = self.user_session.is_idle(0, self.waiting_minutes)
        if is_idle:
            self.waiting_minutes = max(self.max_waiting_minutes, self.waiting_minutes + random.randint(3, 5))
        else:
            self.waiting_minutes = random.randint(3, 5)
        return is_idle

    async def generate_message(self) -> Message:
        message = await ai_service_async.generate_reply(self.user_session, self.prompt)
        return message

