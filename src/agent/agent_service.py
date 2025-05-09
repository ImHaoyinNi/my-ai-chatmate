import asyncio
import base64
import io
import random
import time

from src.api.aws_api import aws_api_async
from src.api.interface.image2text_api_interface import Image2TextAPIInterfaceAsync
from src.api.interface.llm_api_interface import LLMAPIInterfaceAsync
from src.api.interface.speech2text_api_interface import Speech2TextAPIInterfaceAsync
from src.api.interface.text2image_api_interface import Text2ImageAPIInterfaceAsync
from src.api.interface.tts_api_interface import TTSAPIInterface
from src.api.local_image_generator_api import local_image_generator_api
from src.api.nvidia_playground_api_async import nvidia_playground_api_async
from src.api.openai_api import openai_api
from src.data.Message import MessageType, Message, chat_message_store
from src.agent.user_session import UserSession
from src.utils.constants import new_message, Role
from src.utils.logger import logger
from src.utils.utils import remove_think_tag, get_image_prompt, remove_image_prompt, remove_quotes


class AgentService:
    def __init__(self):
        self.llm_api: LLMAPIInterfaceAsync = nvidia_playground_api_async
        self.tts_api: TTSAPIInterface = aws_api_async
        self.image2text_api: Image2TextAPIInterfaceAsync = nvidia_playground_api_async
        self.speech2text_api: Speech2TextAPIInterfaceAsync = openai_api
        self.text2image_api: Text2ImageAPIInterfaceAsync = nvidia_playground_api_async

    async def generate_reply(self, user_session: UserSession, user_message: str,
                             expected_message_type: MessageType = MessageType.ANY) -> Message:
        user_session.add_user_context(user_message)
        memories = user_session.recall_memory(user_message)
        ai_reply: str = await self.generate_text_response(user_session)
        ai_reply = remove_think_tag(ai_reply)
        user_session.add_bot_context(ai_reply)
        image_prompt = get_image_prompt(ai_reply)
        if image_prompt != "":
            ai_reply = remove_image_prompt(ai_reply)
        ai_reply = remove_quotes(ai_reply)

        try:
            match expected_message_type:
                case MessageType.ANY:
                    # Voice: 15% chance of sending voice message
                    if user_session.reply_with_voice and random.random() < 0.15:
                        voice = await self.tts_api.text_to_speech(ai_reply, "Ruth")
                        message = Message(MessageType.VOICE, voice, user_message, user_session.user_id)
                        chat_message_store.enqueue(user_session.user_id, message)
                    else:
                        # Text
                        message = Message(MessageType.TEXT, ai_reply, user_message, user_session.user_id)
                        chat_message_store.enqueue(user_session.user_id, message)
                    # Image
                    if image_prompt != "" and user_session.enable_image:
                        image_message = await self.generate_image(user_session, image_prompt)
                        chat_message_store.enqueue(user_session.user_id, image_message)
                    return message
                case MessageType.TEXT:
                    message = Message(MessageType.TEXT, ai_reply, user_message, user_session.user_id)
                    chat_message_store.enqueue(user_session.user_id, message)
                    return message
                case MessageType.VOICE:
                    voice = await self.tts_api.text_to_speech(ai_reply, "Ruth")
                    message = Message(MessageType.VOICE, voice, user_message, user_session.user_id)
                    chat_message_store.enqueue(user_session.user_id, message)
                    return message
                case MessageType.IMAGE:
                    # Image
                    if image_prompt != "" and user_session.enable_image:
                        image_message = await self.generate_image(user_session, image_prompt)
                        chat_message_store.enqueue(user_session.user_id, image_message)
                        return image_message
                    else:
                        return Message(MessageType.NONE, ai_reply, user_message, user_session.user_id)
                case _:
                    logger.error(f"Unknown message type: {expected_message_type}")
                    return Message(MessageType.BAD_MESSAGE, ai_reply, user_message, user_session.user_id)
        except Exception as e:
            logger.error("An error happens when generating reply: " + str(e))
            return Message(MessageType.NONE, ai_reply, user_message, user_session.user_id)

    async def generate_text_response(self, user_session: UserSession) -> str:
        start_time = time.time()
        logger.info(f"====={self.llm_api.api_name} generating text response...")

        res = await self.llm_api.generate_text_response(user_session.context)

        end_time = time.time()
        duration = round(end_time - start_time, 1)
        logger.info(f"====={self.llm_api.api_name} takes {duration} seconds to generate text")
        return res

    async def text2voice(self, user_session: UserSession, text: str) -> io.BytesIO:
        audio_file = await self.tts_api.text_to_speech(text, voice_id="Ruth")
        return audio_file

    async def transcribe(self, voice_buffer: io.BytesIO) -> str:
        text = await self.speech2text_api.speech_to_text(voice_buffer)
        logger.info(f"User said: {text}")
        return text

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

    async def generate_image(self, user_session: UserSession, prompt: str) -> Message:
        start_time = time.time()
        logger.info(f"=====Got an image prompt: {prompt}")
        logger.info(f"====={self.text2image_api.api_name} generating image...")
        try:
            image_b64 = await self.text2image_api.generate_image(prompt)
            image_bytes = base64.b64decode(image_b64)
            image_io = io.BytesIO(image_bytes)

            end_time = time.time()
            duration = round(end_time - start_time, 1)
            logger.info(f"====={self.text2image_api.api_name} takes {duration} seconds to generate image")
            return Message(MessageType.IMAGE, image_io, prompt, user_session.user_id)
        except Exception as e:
            logger.error(e)
            return Message(MessageType.BAD_MESSAGE,
                           f"Your bot tried to send you\n <image_prompt> {prompt} </image_prompt>\n "
                           f"But it got an error: {e}.",
                           prompt,
                           user_session.user_id)

agent_service = AgentService()
async def main():
    session = UserSession(123)
    message1 = await agent_service.generate_reply(session, "What is your name")
    message2 = await agent_service.generate_reply(session, "What is your age")
    message3 = await agent_service.text2voice(session, "I love you!")
    print(message1)
    print(message2)
    print(message3)

if __name__ == '__main__':
    asyncio.run(main())