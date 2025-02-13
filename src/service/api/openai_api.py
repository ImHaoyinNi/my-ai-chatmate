import asyncio
import io
from openai import AsyncOpenAI

from src.service.api.interface.async_interface.llm_api_interface_async import LLMAPIInterfaceAsync
from src.service.api.interface.async_interface.speech2text_api_interface_async import Speech2TextAPIInterfaceAsync
from src.utils.config import config
from src.utils.constants import new_message, Role
from src.utils.logger import logger


class OpenAIAPI(Speech2TextAPIInterfaceAsync, LLMAPIInterfaceAsync):
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
        logger.info(f"User said: {transcription.text}")
        return transcription.text

    async def generate_text_response(self, context: list[dict]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=context,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            raise

openai_api = OpenAIAPI(api_key=config.openai_api_key)

async def main() -> None:
    # context.append(new_message(Role.USER, "hello babe 😘"))
    # context.append(new_message(Role.USER, "hello babe 😘"))
    # context.append(new_message(Role.USER, "hello babe 😘"))
    # context.append(new_message(Role.USER, "hello babe 😘"))
    # context.append(new_message(Role.USER, "hello babe 😘"))
    await openai_api.speech_to_text(speech=io.BytesIO())


if __name__ == "__main__":
    asyncio.run(main())
