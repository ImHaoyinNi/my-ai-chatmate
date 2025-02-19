from src.service.ai_service.ai_service_async import ai_service_async
from src.service.behavior.active_behaviors.base_active_behavior import BaseActiveBehavior
from src.service.message_processor.Message import Message
from src.service.user_session import UserSession
from src.utils.utils import get_current_time


class StartConversation(BaseActiveBehavior):
    def __init__(self, user_session: UserSession, bot):
        super(StartConversation, self).__init__(user_session, bot, name="Start Conversation")
        self.prompt = (
            "I didn't reply your message for a while. "
            "Based on your persona, feel free to take the lead and start a conversation with me. "
            "Ask questions or share thoughts that fit your character's traits, background, and style. "
            "Let's get into a natural flow where your persona can interact with me, and I'll respond in kind."
        )

    def to_continue(self) -> bool:
        is_idle = self.user_session.is_idle(6, 0)
        if not is_idle:
            return False
        hour, _ = get_current_time()
        if 0 <= hour <= 7:
            return False
        else:
            return True

    async def generate_message(self) -> Message:
        print("Generating message.....")
        message = await ai_service_async.generate_reply(self.user_session, self.prompt)
        return message