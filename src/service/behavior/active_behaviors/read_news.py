from sphinx.util import requests

from src.service.ai_service.ai_service_async import ai_service_async
from src.service.behavior.active_behaviors.active_behavior import ActiveBehavior
from src.service.message_processor.Message import Message
from src.service.user_session import UserSession
from src.utils.config import config


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

    async def generate_message(self) -> Message:
        prompt = self.prompt_1 + self._pull_news() + self.prompt_2
        message: Message = await ai_service_async.generate_reply(self.user_session, prompt)
        return message

    # TODO: Make it async
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