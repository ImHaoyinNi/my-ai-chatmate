import io
from openai import AsyncOpenAI

from src.service.api.interface.async_interface.speech2text_api_interface_async import Speech2TextAPIInterfaceAsync
from src.utils.config import config


class OpenAIAPI(Speech2TextAPIInterfaceAsync):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    @property
    def api_name(self) -> str:
        return "OpenAI API"

    async def speech_to_text(self, speech: io.BytesIO) -> str:
        transcription = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=speech
        )
        print(transcription.text)
        return transcription.text

openai_api = OpenAIAPI(api_key=config.openai_api_key)

async def main() -> None:
    await openai_api.speech_to_text(speech=io.BytesIO())
