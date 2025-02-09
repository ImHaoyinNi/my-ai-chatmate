import io
from src.service.ai_service import aiService
from src.service.commands import run_command
from src.service.message_processor.Message import Message
from src.service.user_session import UserSessionManager


class MessageProcessor:
    @staticmethod
    def process_text(user_id: int, text: str) -> Message:
        user_session = UserSessionManager.get_session(user_id)
        response = aiService.generate_reply(user_session, text)
        return response

    @staticmethod
    def process_voice(user_id: int, voice_buffer: io.BytesIO):
        text = aiService.transcribe(voice_buffer)
        user_session = UserSessionManager.get_session(user_id)
        response = aiService.generate_reply(user_session, text)
        return response

    @staticmethod
    def process_image(user_id, image_b64: str):
        user_session = UserSessionManager.get_session(user_id)
        description = aiService.describe_image(user_session, image_b64)
        prompt = "I sent you an image. Here is the description of the image: \n" + description
        return aiService.generate_reply(user_session, prompt)

    @staticmethod
    def process_command(user_id, command) -> str:
        if " " in command:
            command, arguments = command.split(" ")
        else:
            command, arguments = command, ""
        arguments = arguments.lower()
        arguments = arguments.split(" ")
        return run_command(user_id, command, arguments)

if __name__ == '__main__':
    user_id = 12345
    res = MessageProcessor.process_text(user_id, 'How many states in USA')
    print(res)
    res = MessageProcessor.process_text(user_id, 'What are they?')
    print(res)
    user_session = UserSessionManager.get_session(user_id)
    print(user_session.context)