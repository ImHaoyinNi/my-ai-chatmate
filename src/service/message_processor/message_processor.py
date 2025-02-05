import io
from src.service.ai_service import aiService
from src.service.commands import run_command
from src.service.message_processor.Reply import Reply
from src.service.user_session import UserSessionManager


class MessageProcessor:
    @staticmethod
    def process_text(user_id, text) -> Reply:
        user_session = UserSessionManager.get_session(user_id)
        response = aiService.generate_reply(user_session, text)
        return response

    @staticmethod
    def process_voice(user_id, voice_buffer: io.BytesIO):
        text = aiService.transcribe(voice_buffer)
        user_session = UserSessionManager.get_session(user_id)
        response = aiService.generate_reply(user_session, text)
        return response

    @staticmethod
    def process_image(user_id, image_file):
        return f"I see: image"

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