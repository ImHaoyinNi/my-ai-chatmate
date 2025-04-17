import httpx
import asyncio
from openai import AsyncOpenAI

from src.api.interface.image2text_api_interface import Image2TextAPIInterfaceAsync
from src.api.interface.llm_api_interface import LLMAPIInterfaceAsync
from src.api.interface.text2image_api_interface import Text2ImageAPIInterfaceAsync
from src.utils.config import config
from src.utils.constants import new_message, Role


class NvidiaPlaygroundAPIAsync(LLMAPIInterfaceAsync, Image2TextAPIInterfaceAsync, Text2ImageAPIInterfaceAsync):
    @property
    def api_name(self):
        return "Nvidia Playground API"

    def __init__(self, api_url, llm_name, image2text_api_url, text2image_api_url):
        self._text_model = llm_name
        self._api_url = api_url
        self._api_name = "nvidia playground"
        self._api_key = config.nvidia_api_key
        self.client = AsyncOpenAI(
            base_url=self._api_url,
            api_key=self._api_key
        )
        self._image2text_api_url = image2text_api_url
        self._text2image_api_url = text2image_api_url

    async def generate_text_response(self, context: list[dict]) -> str:
        completion = await self.client.chat.completions.create(
            model=self._text_model,
            messages=context,
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            stream=False
        )
        try:
            return completion.choices[0].message.content
        except Exception:
            return f"Bad response from {self.api_name}"

    async def describe_image(self, context: list[dict], image_b64: str) -> str:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
            payload = {
                "model": 'meta/llama-3.2-90b-vision-instruct',
                "messages": [{"role": "user", "content": f'What is in this image? <img src="data:image/png;base64,{image_b64}" />'}],
                "max_tokens": 512,
                "temperature": 1.00,
                "top_p": 1.00,
                "stream": False
            }
            response = await client.post(self._image2text_api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def generate_image(self, pos: str, neg: str = "") -> str:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
            payload = {
                "text_prompts": [{"text": pos, "weight": 1}, {"text": neg, "weight": -1}],
                "cfg_scale": 5,
                "sampler": "K_DPM_2_ANCESTRAL",
                "seed": 0,
                "steps": 25
            }
            response = await client.post(self._text2image_api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["artifacts"][0]["base64"]

    async def generate_image_consistory(self, subject_prompt, scene_prompt1, scene_prompt2, neg_prompt="", style_prompt="A photo of") -> str:
        async with httpx.AsyncClient() as client:
            invoke_url = "https://ai.api.nvidia.com/v1/genai/nvidia/consistory"
            headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
            payload = {
                "mode": 'init',
                "subject_prompt": subject_prompt,
                "subject_tokens": ["woman", "dress"],
                "subject_seed": 43,
                "style_prompt": style_prompt,
                "scene_prompt1": scene_prompt1,
                "scene_prompt2": scene_prompt2,
                "negative_prompt": neg_prompt,
                "cfg_scale": 5,
                "same_initial_noise": False
            }
            response = await client.post(invoke_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["artifacts"][0]["base64"]

nvidia_playground_api_async = NvidiaPlaygroundAPIAsync(
    api_url=config.nvidia_api_settings["llm_api_url"],
    llm_name=config.nvidia_api_settings["llm_name"],
    image2text_api_url=config.nvidia_api_settings["image2text_api_url"],
    text2image_api_url=config.nvidia_api_settings["text2image_api_url"]
)

async def main():
    context = [new_message(Role.USER, "What is your name?")]
    img = await nvidia_playground_api_async.generate_image("A cat drinking coffee")
    res = await nvidia_playground_api_async.generate_text_response(context)
    print(res)
    print(img)

if __name__ == '__main__':
    asyncio.run(main())
