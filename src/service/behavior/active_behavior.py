import asyncio
import os

import py_trees
import requests
from dotenv import load_dotenv

from src.service.ai_service import aiService
from src.service.logger import logger
from src.service.message_processor.Message import Message, MessageType
from src.service.user_session import UserSession

class ActiveBehavior(py_trees.behaviour.Behaviour):
    def __init__(self, user_session: UserSession, bot, name="Base Send Message"):
        super(ActiveBehavior, self).__init__(name=name)
        self.user_session = user_session
        self.bot = bot
        self.logger = py_trees.logging.Logger(name=self.name)
        self._running_task = None

    def generate_message(self) -> Message:
        raise NotImplementedError

    async def send_content(self, reply: Message):
        match reply.message_type:
            case MessageType.TEXT:
                await self.bot.send_message(chat_id=self.user_session.user_id, text=reply.content)
            case MessageType.VOICE:
                await self.bot.send_voice(chat_id=self.user_session.user_id, voice=reply.content)
            case _:
                await self.bot.send_message(chat_id=self.user_session.user_id, text="Bad reply")

    def update(self):
        logger.info(f"Behavior update: {self.name}")
        try:
            if not self.user_session.is_idle(0, 1):
                return py_trees.common.Status.FAILURE
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
        self.prompt = (
            "I didn't reply your message for a while. "
            "Based on your persona, feel free to take the lead and start a conversation with me. "
            "Ask questions or share thoughts that fit your character's traits, "
            "background, and style. "
            "Let's get into a natural flow where your persona can interact with me, and I'll respond in kind."
        )

    def generate_message(self) -> Message:
        text = aiService.generate_text_response(self.user_session, self.prompt)
        if self.user_session.reply_with_voice:
            voice = aiService.generate_voice_response(self.user_session, text)
            return Message(MessageType.VOICE, voice)
        return Message(MessageType.TEXT, text)

class ReadNews(ActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(ReadNews, self).__init__(user_session, bot, name="Read News")
        self.prompt_1 = "This is some latest news. "
        self.prompt_2 = (
            "Based on your persona, feel free to take the lead and start a conversation with me. "
            "Ask questions or share thoughts that fit your character's traits, background and style. "
            "Let's get into a natural flow where your persona can interact with me, and I'll respond in kind."
        )
        load_dotenv()
        self._api_key = os.getenv("GNEWS_API_KEY")

    def generate_message(self) -> Message:
        prompt = self.prompt_1 + self._pull_news() + self.prompt_2
        text = aiService.generate_text_response(self.user_session, prompt)
        return Message(MessageType.TEXT, text)

    def _pull_news(self) -> str:
        params = {"country": "us", "token": self._api_key, "lang": "en"}
        response = requests.get("https://gnews.io/api/v4/top-headlines", params=params)
        data = response.json()
        if "articles" in data:
            summaries = []
            for article in data["articles"][:3]:  # Get top 3 news articles
                title = article["title"]
                description = article.get("description", "")
                summaries.append(f"- {title}: {description}")
            return "\n".join(summaries)
        else:
            return "No news available at the moment."

if __name__ == "__main__":
    a = ReadNews(user_session=UserSession(123), bot=None)
    a.generate_message()