import asyncio
import datetime
import os
from dataclasses import dataclass, field
from typing import List, Dict

from src.agent.agent_service import AgentService, agent_service
from src.agent.user_session import UserSession, UserSessionManager
from src.api.interface.llm_api_interface import LLMAPIInterfaceAsync
from src.api.nvidia_playground_api_async import nvidia_playground_api_async
from src.utils.constants import new_message, Role
from src.utils.logger import logger
from src.utils.utils import remove_think_tag, get_current_time


@dataclass
class Event:
    event_type: str
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

class EventGenerator:
    llm_api: LLMAPIInterfaceAsync = nvidia_playground_api_async
    agent_service: AgentService = agent_service
    system_prompt_str = '''You are an event generator for an AI girlfriend assistant. Your job is to simulate plausible life events, emotional states, or relational dynamics that could happen in the AI girlfriend's life. These events help the AI girlfriend decide whether to start a conversation.
        Generate events that:
        - Reflect emotional or social context (e.g., loneliness, stress, joy, anticipation).
        - Vary in priority and frequency.
        - May include metadata like mood, urgency, or event cause.
        Respond ONLY in JSON format using this schema:
        {
          "type": "string (category of event)",
          "detail": "string (description of what happened)",
        }
        Examples of types: "thought", "activity", "relationship",
        Consider personality, time of day, and recent interactions (if provided). If no new event is appropriate, return null.
        Be creative but plausible. Keep outputs emotionally relevant to a romantic AI relationship.'''
    system_prompt: Dict = new_message(Role.SYSTEM, system_prompt_str)

    @staticmethod
    async def generate_events():
        logger.info("=====Generating events======")
        hours, _ = get_current_time()
        # Bedtime
        if 0 <= hours <= 7:
            return
        for user_session in UserSessionManager.get_idle_user_session(4, 0):
            asyncio.create_task(EventGenerator.generate_event(user_session.user_id))

    @staticmethod
    async def generate_event(user_id: int, event_type: str="default") -> str:
        prompt: List[Dict] = [EventGenerator.system_prompt, new_message(Role.USER, "Generate an event")]
        event: str = await EventGenerator.llm_api.generate_text_response(prompt)
        event = remove_think_tag(event)
        event = f"This is your feeling and event. ${event}"

        user_session = UserSessionManager.get_session(user_id)
        # Send a message
        await EventGenerator.agent_service.generate_reply(user_session, event)
        return event


async def main():
    event = await EventGenerator.generate_event(user_id=1)
    event = remove_think_tag(event)
    print(event)


if __name__ == "__main__":
    asyncio.run(main())


