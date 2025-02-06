import asyncio

import py_trees

from src.service.ai_service import aiService
from src.service.message_processor.Reply import Reply, ReplyType
from src.service.user_session import UserSession


class ActiveBehavior(py_trees.behaviour.Behaviour):
    def __init__(self, user_session: UserSession, bot, name="Base Send Message"):
        super(ActiveBehavior, self).__init__(name=name)
        self.user_session = user_session
        self.bot = bot
        self.logger = py_trees.logging.Logger(name=self.name)
        self._running_task = None

    def generate_message(self) -> Reply:
        """Override this method in child classes to provide specific content"""
        raise NotImplementedError

    async def send_content(self, reply: Reply):
        match reply.reply_type:
            case ReplyType.TEXT:
                await self.bot.send_message(chat_id=self.user_session.user_id, text=reply.content)
            case ReplyType.VOICE:
                await self.bot.send_voice(chat_id=self.user_session.user_id, voice=reply.content)
            case _:
                await self.bot.send_message(chat_id=self.user_session.user_id, text="Bad reply")

    def update(self):
        self.logger.debug("Attempting to send message")
        try:
            reply = self.generate_message()
            loop = asyncio.get_event_loop()
            self._running_task = loop.create_task(self.send_content(reply))
            self._running_task.add_done_callback(self._on_message_complete)
            return py_trees.common.Status.RUNNING
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return py_trees.common.Status.FAILURE

    def _on_message_complete(self, future):
        try:
            future.result()
            return py_trees.common.Status.SUCCESS
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            return py_trees.common.Status.FAILURE


class SendTextMessage(ActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(SendTextMessage, self).__init__(user_session, bot, name="Send Text Message")
        self.user_prompt = (
            "I didn't reply your message for a while. "
            "Based on your persona, feel free to take the lead and start a conversation with me. "
            "Ask questions or share thoughts that fit your character's traits, "
            "background, and style. "
            "Let's get into a natural flow where your persona can interact with me, and I'll respond in kind."
        )

    def generate_message(self) -> Reply:
        text = aiService.generate_text_response(self.user_session, self.user_prompt)
        return Reply(ReplyType.TEXT, text)