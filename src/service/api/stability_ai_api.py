import configparser
from dataclasses import dataclass

import aiohttp
import base64
import json
from typing import Optional, Dict, Any

import httpx
from aiohttp import FormData

from src.service.api.interface.async_interface.text2image_api_interface_async import Text2ImageAPIInterfaceAsync
from src.utils.config import config
from src.utils.logger import logger


@dataclass
class ImageGenerationConfig:
    prompt: str
    output_format: str = "webp"
    model_id_v2: str = "stable-diffusion-xl-1024-v1-0"
    width: int = 1024
    height: int = 1024
    steps: int = 30
    cfg_scale: float = 7.0
    samples: int = 1

class StabilityAIAPI(Text2ImageAPIInterfaceAsync):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host_v1 = "https://api.stability.ai"
        self.api_host_v2 = "https://api.stability.ai/v2beta"
        self.headers_v1 = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.headers_v2 = {
            "authorization": f"Bearer {self.api_key}",
            "accept": "image/*"
        }
        self.version = config.stability_ai_api_settings["version"]

    @property
    def api_name(self) -> str:
        return "Stability AI API"

    async def generate_image(self, prompt: str) -> str:
        if self.version == "v1":
            return await self.generate_image_v1(prompt)
        else:
            return await self.generate_image_v2(prompt)

    async def generate_image_v2(self, prompt) -> Optional[str]:
        url = f"{self.api_host_v2}/stable-image/generate/core"
        try:
            data = {
                "prompt": prompt,
                "output_format": "webp",
            }
            files = {"none": ''}

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers_v2, data=data, files=files)
                if response.status_code == 200:
                    content = response.read()
                    return base64.b64encode(content).decode('utf-8')
                else:
                    error_json = response.json()
                    raise Exception(f"API Error: {error_json}")
        except Exception as e:
            logger.error(f"An error occurred when generating image: {str(e)}")
            raise Exception(f"An error occurred when generating image: {str(e)}")

    async def generate_image_v1(self, prompt: str) -> Optional[str]:
        try:
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7.0,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.api_host_v1}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                        headers=self.headers_v1,
                        json=payload
                ) as response:
                    if response.status != 200:
                        error_detail = await response.text()
                        print(f"Error: {response.status}, Details: {error_detail}")
                        return None

                    response_data = await response.json()
                    if "artifacts" in response_data and len(response_data["artifacts"]) > 0:
                        return response_data["artifacts"][0]["base64"]
                    return None

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return None


stability_ai_api = StabilityAIAPI(api_key=config.stability_ai_api_key)

async def main():
    prompt = "A young sexy blonde woman with big boobs and ear rings and long black ponytail in baseball uniform, athletic build, natural makeup, sweaty but smiling, locker room mirror selfie, wearing golden snitch necklace, warm lighting, unreal engine"
    prompt2 = " A woman with long black ponytail wearing an oversized sweater, stirring a pot in cozy kitchen, soft golden lighting, steam rising, natural makeup with flushed cheeks, anime-style rendering"
    base64_image = await stability_ai_api.generate_image(prompt=prompt2)

    if base64_image:
        with open("generated_image.png", "wb") as f:
            f.write(base64.b64decode(base64_image))
        print("Image generated successfully!")
    else:
        print("Failed to generate image")


# Run the example
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())