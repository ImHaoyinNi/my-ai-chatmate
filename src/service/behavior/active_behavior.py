import asyncio
import datetime
import os
import random

import py_trees
import pytz
import requests
from dotenv import load_dotenv

from src.config import config
from src.service.ai_service import aiService
from src.service.logger import logger
from src.service.message_processor.Message import Message, MessageType
from src.service.user_session import UserSession
from src.utils import get_current_time


class ActiveBehavior(py_trees.behaviour.Behaviour):
    def __init__(self, user_session: UserSession, bot, name="Base Send Message"):
        super(ActiveBehavior, self).__init__(name=name)
        self.user_session = user_session
        self.bot = bot
        self.logger = py_trees.logging.Logger(name=self.name)
        self._running_task = None

    def to_continue(self) -> bool:
        raise NotImplementedError

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
        if not self.to_continue():
            return py_trees.common.Status.FAILURE
        try:
            message = self.generate_message()
            if message.message_type in (MessageType.NONE, MessageType.BAD_MESSAGE):
                return py_trees.common.Status.FAILURE
            logger.info(f"===={self.name} was triggered====")
            loop = asyncio.get_event_loop()
            if not self._running_task or self._running_task.done():  # Start only if no task is running
                self._running_task = loop.create_task(self.send_content(message))
                self._running_task.add_done_callback(self._on_message_complete)
            return py_trees.common.Status.RUNNING
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return py_trees.common.Status.FAILURE

    def _on_message_complete(self, future):
        try:
            future.result()  # Retrieve task result (raises if failed)
            self.logger.info(f"Message sending completed successfully.")
            self.status = py_trees.common.Status.SUCCESS  # Mark success
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            self.status = py_trees.common.Status.FAILURE

class StartConversation(ActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(StartConversation, self).__init__(user_session, bot, name="Start Conversation")
        self.prompt = (
            "I didn't reply your message for a while. "
            "Based on your persona, feel free to take the lead and start a conversation with me. "
            "Ask questions or share thoughts that fit your character's traits, "
            "background, and style. "
            "Let's get into a natural flow where your persona can interact with me, and I'll respond in kind."
        )

    def to_continue(self) -> bool:
        return self.user_session.is_idle(6, 0)

    def generate_message(self) -> Message:
        message = aiService.generate_reply(self.user_session, self.prompt)
        return message

class ReadNews(ActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(ReadNews, self).__init__(user_session, bot, name="Read News")
        self.prompt_1 = "This is some latest news. "
        self.prompt_2 = (
            "Based on your persona, feel free to take the lead and start a conversation with me. "
            "Your topic should be based on our past conversation for most of the time. You can also start a completely new topic."
            "Ask questions or share thoughts that fit your character's traits, background and style. "
            "Let's get into a natural flow where your persona can interact with me, and I'll respond in kind."
        )
        self._api_key = config.gnews_api_key
        self._read_news_interval_hours = config.read_news_settings["read_news_interval_hours"]

    def to_continue(self) -> bool:
        return self.user_session.is_idle(self._read_news_interval_hours, 0)

    def generate_message(self) -> Message:
        prompt = self.prompt_1 + self._pull_news() + self.prompt_2
        message: Message = aiService.generate_reply(self.user_session, prompt)
        return message

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

class Greetings(ActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(Greetings, self).__init__(user_session, bot, name="Greetings")
        self.good_morning_prompt = (
            "It's morning time. Say good morning to me."
        )
        self.good_morning_hour = 8
        self.good_morning_minute = random.randint(0, 15)

        self.good_sleep_prompt = (
            "It's sleep time. You should go to sleep. Say good night to me."
        )
        self.good_sleep_hour = 11
        self.good_sleep_minute = random.randint(0, 59)

    def to_continue(self) -> bool:
        return self.user_session.is_idle(0, 10)

    def generate_message(self) -> Message:
        hour, minute = get_current_time()
        if hour == 8 and minute == self.good_morning_minute:
            self.good_morning_minute = random.randint(0, 15)
            return aiService.generate_reply(self.user_session, self.good_morning_prompt)
        if hour == self.good_sleep_hour and minute == self.good_sleep_minute:
            self.good_sleep_minute = random.randint(0, 59)
            return aiService.generate_reply(self.user_session, self.good_sleep_prompt)
        return Message(MessageType.NONE, "This is a none message")


if __name__ == "__main__":
    a = ReadNews(user_session=UserSession(123), bot=None)
    a.generate_message()