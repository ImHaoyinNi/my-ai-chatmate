import asyncio
import io

from src.service.ai_service.ai_service_async import ai_service_async
from src.service.commands import run_command
from src.service.message_processor.Message import Message
from src.service.user_session import UserSessionManager


class MessageProcessorAsync:
    async def process_text(user_id: int, text: str) -> Message:
        user_session = UserSessionManager.get_session(user_id)
        response = await ai_service_async.generate_reply(user_session, text)
        return response

    @staticmethod
    async def process_voice(user_id: int, voice_buffer: io.BytesIO) -> Message:
        text = await ai_service_async.transcribe(voice_buffer)
        user_session = UserSessionManager.get_session(user_id)
        response = await ai_service_async.generate_reply(user_session, text)
        return response

    @staticmethod
    async def process_image(user_id, image_b64: str) -> Message:
        user_session = UserSessionManager.get_session(user_id)
        description = ai_service_async.describe_image(user_session, image_b64)
        prompt = "I sent you an image. Here is the description of the image: \n" + description
        res = await ai_service_async.generate_reply(user_session, prompt)
        return res

    @staticmethod
    def process_command(user_id, command) -> str:
        if " " in command:
            command, arguments = command.split(" ")
        else:
            command, arguments = command, ""
        arguments = arguments.lower()
        arguments = arguments.split(" ")
        return run_command(user_id, command, arguments)


async def main():
    user_id = 12345
    res = await MessageProcessorAsync.process_text(user_id, 'How many states in USA')
    print(res)
    res = await MessageProcessorAsync.process_text(user_id, 'What are they?')
    print(res)
    user_session = UserSessionManager.get_session(user_id)
    print(user_session.context)

if __name__ == '__main__':
    asyncio.run(main())