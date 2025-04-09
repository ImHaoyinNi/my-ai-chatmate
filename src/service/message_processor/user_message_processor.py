import asyncio
import io

from src.data.user_info import UserInfo, verify_user
from src.service.ai_service import ai_service
from src.service.commands import run_command
from src.service.message_processor.Message import Message, chat_message_store, MessageType
from src.service.user_session import UserSessionManager
from src.utils.constants import UserRole


class UserMessageProcessor:
    @staticmethod
    async def process_text(user_info: UserInfo, text: str) -> Message:
        user_session = UserSessionManager.get_session(user_info.user_id)
        if verify_user(user_info):
            response = await ai_service.generate_reply(user_session, text)
            return response
        else:
            return UserMessageProcessor.enqueue_bad_message(user_info)

    @staticmethod
    async def process_voice(user_info: UserInfo, voice_buffer: io.BytesIO) -> Message:
        user_session = UserSessionManager.get_session(user_info.user_id)
        if verify_user(user_info):
            text = await ai_service.transcribe(voice_buffer)
            response = await ai_service.generate_reply(user_session, text)
            return response
        else:
            return UserMessageProcessor.enqueue_bad_message(user_info)

    @staticmethod
    async def process_image(user_info: UserInfo, image_b64: str) -> Message:
        user_session = UserSessionManager.get_session(user_info.user_id)
        if verify_user(user_info):
            description = await ai_service.describe_image(user_session, image_b64)
            prompt = "I sent you an image. Here is the description of the image: \n" + description
            res = await ai_service.generate_reply(user_session, prompt)
            return res
        else:
            return UserMessageProcessor.enqueue_bad_message(user_info)

    @staticmethod
    def process_command(user_id, command) -> str:
        if " " in command:
            command, arguments = command.split(" ")
        else:
            command, arguments = command, ""
        arguments = arguments.lower()
        arguments = arguments.split(" ")
        return run_command(user_id, command, arguments)

    @staticmethod
    def enqueue_bad_message(user_info: UserInfo) -> Message:
        message: Message = Message(MessageType.BAD_MESSAGE,
                                   f"Bot cannot reply to your message.\n"
                                   f"Your credits: {user_info.credits}.\n"
                                   f"Your role: {user_info.role}",
                                   "",
                                   user_info.user_id)
        chat_message_store.enqueue(user_info.user_id, message)
        return message

async def main(datetime=None):
    user_info: UserInfo = UserInfo(
        user_id=123,
        has_subscribed=True,
        user_name="",
        phone_number="",
        credits=1000,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        role=UserRole.REGULAR.value,
        gender="male"
    )
    res = await UserMessageProcessor.process_text(user_info, 'How many states in USA')
    print(res)
    res = await UserMessageProcessor.process_text(user_info, 'What are they?')
    print(res)
    user_session = UserSessionManager.get_session(user_info.user_id)
    print(user_session.context)

if __name__ == '__main__':
    asyncio.run(main())