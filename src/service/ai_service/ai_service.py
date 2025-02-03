import io

from src.service.api.ollama_api import ollama_api
from src.service.user_session.user_session import UserSession
from src.utils import remove_think_tag


class AIService:
    def __init__(self):
        self.llm_api = ollama_api
        self.audio_api = ollama_api

    def generate_response(self, user_session: UserSession, text) -> str:
        res = self.generate_text_response(user_session, text)
        res = remove_think_tag(res)
        if user_session.reply_with_voice:
            return self.llm_api.text2audio(res)
        else:
            return res

    def generate_text_response(self, user_session: UserSession, text) -> str:
        user_session.add_user_context(text)
        res = self.llm_api.generate_text_response(user_session.context)
        res = remove_think_tag(res)
        user_session.add_bot_context(res)
        return res

    def transcribe(self, voice_buffer: io.BytesIO):
        return self.audio_api.transcribe(voice_buffer)

    def generate_voice_response(self, user_session: UserSession, text) -> io.BytesIO:
        text = "I love you!"
        audio_file = self.audio_api.text2audio(text)
        return audio_file

aiService = AIService()

if __name__ == "__main__":
    user_session = UserSession(123)
    res = aiService.generate_response(user_session, 'How many states in USA')
    print(res)



