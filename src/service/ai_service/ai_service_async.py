import asyncio
import io
import time
from src.service.api.aws_api import aws_api
from src.service.api.interface.async_interface.image2text_api_interface_async import Image2TextAPIInterfaceAsync
from src.service.api.interface.async_interface.llm_api_interface_async import LLMAPIInterfaceAsync
from src.service.api.interface.sync.tts_api_interface import TTSAPIInterface
from src.service.api.nvidia_playground_api_async import nvidia_playground_api_async
from src.service.message_processor.Message import MessageType, Message
from src.service.user_session import UserSession
from src.utils.constants import new_message, Role
from src.utils.logger import logger
from src.utils.utils import remove_think_tag


class AiServiceAsync:
    def __init__(self):
        self.llm_api: LLMAPIInterfaceAsync = nvidia_playground_api_async
        self.tts_api: TTSAPIInterface = aws_api
        self.image2text_api: Image2TextAPIInterfaceAsync = nvidia_playground_api_async

    async def generate_reply(self, user_session: UserSession, prompt: str,
                             message_type: MessageType = MessageType.ANY) -> Message:
        user_session.add_user_context(prompt)
        ai_reply: str = await self.generate_text_response(user_session)
        ai_reply = remove_think_tag(ai_reply)
        user_session.add_bot_context(ai_reply)

        if message_type == MessageType.ANY:
            if user_session.reply_with_voice:
                voice = self.tts_api.text_to_speech(ai_reply, "Ruth")
                return Message(MessageType.VOICE, voice)
            else:
                return Message(MessageType.TEXT, ai_reply)
        elif message_type == MessageType.TEXT:
            return Message(MessageType.TEXT, ai_reply)
        elif message_type == MessageType.VOICE:
            voice = self.tts_api.text_to_speech(ai_reply, "Ruth")
            return Message(MessageType.VOICE, voice)
        elif message_type == MessageType.IMAGE:
            # TODO: Implement image message
            return Message(MessageType.TEXT, ai_reply)
        else:
            return Message(MessageType.TEXT, ai_reply)

    async def generate_text_response(self, user_session: UserSession) -> str:
        start_time = time.time()
        logger.info(f"{self.llm_api.api_name} generating text response...")

        res = await self.llm_api.generate_text_response(user_session.context)

        end_time = time.time()
        duration = round(end_time - start_time, 1)
        logger.info(f"{self.llm_api.api_name} takes {duration} seconds to generate text")
        return res

    async def text2voice(self, user_session: UserSession, text: str) -> io.BytesIO:
        # TODO: Make it async
        audio_file = self.tts_api.text_to_speech(text, voice_id="Ruth")
        return audio_file

    async def transcribe(self, voice_buffer: io.BytesIO):
        # TODO: Implement transcribe
        return await self.tts_api.transcribe(voice_buffer)

    async def describe_image(self, user_session, image_b64: str):
        logger.info(f"{self.llm_api.api_name} describing image...")
        start_time = time.time()

        description = await self.image2text_api.describe_image(user_session, image_b64)

        end_time = time.time()
        duration = round(end_time - start_time, 1)
        logger.info(f"{self.llm_api.api_name} takes {duration} seconds to describe image")
        return description

    async def chat2sd_prompt(self, user_session: UserSession) -> str:
        context: list[dict] = user_session.context
        llm_query = f"""
        Generate a detailed Stable Diffusion image prompt based on this conversation. Include:
        1. Subject: Age, appearance, clothing (from system message).
        2. Action: What they're doing (from assistant's message).
        3. Setting: Environment inferred from context.
        4. Style: Realistic, anime, etc. Default to "realistic" if unspecified.
        5. Details: Lighting, camera angle, mood.

        Conversation:
        {context}

        Prompt:
        """
        res = await self.llm_api.generate_text_response([new_message(Role.USER, llm_query)])
        res = remove_think_tag(res)
        return res

ai_service_async = AiServiceAsync()
async def main():
    session = UserSession(123)
    message1 = await ai_service_async.generate_reply(session, "What is your name")
    message2 = await ai_service_async.generate_reply(session, "What is your age")
    message3 = await ai_service_async.text2voice(session, "I love you!")
    print(message1)
    print(message2)
    print(message3)

if __name__ == '__main__':
    asyncio.run(main())