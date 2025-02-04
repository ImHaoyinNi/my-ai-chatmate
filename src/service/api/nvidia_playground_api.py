import os

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

from src.service.api.text_api_interface import TextAPIInterface
from dotenv import load_dotenv

class NvidiaPlaygroundAPI(TextAPIInterface):
    @property
    def api_name(self):
        return "Nvidia Playground API"

    def __init__(self, text_model="deepseek-ai/deepseek-r1", api_url="https://integrate.api.nvidia.com/v1"):
        self._text_model = text_model
        self.api_url = api_url
        self._api_name = "nvidia playground"
        load_dotenv()
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.client = OpenAI(
            base_url=self.api_url,
            api_key=self.api_key
        )

    def generate_text_response(self, context: list[dict]) -> str:
        completion = self.client.chat.completions.create(
            model=self._text_model,
            messages=context,
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            stream=False
        )
        return completion.choices[0].message.content

nvdia_playground_api = NvidiaPlaygroundAPI()