import io
import random
import time

from src.service.api.nvidia_playground_api import nvdia_playground_api
from src.service.api.ollama_api import ollama_api
from src.service.api.text_api_interface import TextAPIInterface
from src.service.api.voice_api_interface import VoiceAPIInterface
from src.service.user_session import UserSession
from src.utils import remove_think_tag


class AIService:
    def __init__(self):
        self.text_api: TextAPIInterface = nvdia_playground_api
        self.voice_api: VoiceAPIInterface = ollama_api

    def generate_response(self, user_session: UserSession, text) -> str | io.BytesIO:
        res = self.generate_text_response(user_session, text)

        res = remove_think_tag(res)
        if user_session.reply_with_voice:
            return self.voice_api.text2audio(res)
        else:
            return res

    def generate_text_response(self, user_session: UserSession, prompt: str) -> str:
        user_session.add_user_context(prompt)
        start_time = time.time()
        print(f"{self.text_api.api_name} generating text response...")
        res = self.text_api.generate_text_response(user_session.context)
        end_time = time.time()
        duration = round(end_time - start_time, 1)
        print(f"{self.text_api.api_name} takes {duration} seconds to generate")
        res = remove_think_tag(res)
        user_session.add_bot_context(res)
        return res

    def generate_voice_response(self, user_session: UserSession, text) -> io.BytesIO:
        text = "I love you!"
        audio_file = self.voice_api.text2audio(text)
        return audio_file

    def generate_greetings(self, user_session: UserSession) -> str | io.BytesIO:
        templates = [
            "早安亲爱的～☀️今天天气超好，记得吃早餐哦！",
            "早上好呀～🌼我昨晚梦到你了呢～"
        ]
        reply = random.choice(templates)
        if user_session.reply_with_voice:
            return self.voice_api.text2audio(reply)

    def transcribe(self, voice_buffer: io.BytesIO):
        return self.voice_api.transcribe(voice_buffer)


aiService = AIService()

if __name__ == "__main__":
    user_session = UserSession(123)
    res = aiService.generate_response(user_session, 'How many states in USA')
    print(res)



