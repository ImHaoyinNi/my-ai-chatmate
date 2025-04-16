from dataclasses import dataclass
import aiohttp
import base64
from typing import Optional, List
import httpx
import asyncio

from src.service.api.interface.text2image_api_interface import Text2ImageAPIInterfaceAsync
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
        self.available_models: List[str] = ["ultra", "core", "sd3"]
        self.default_model: str = "core"
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
            return await self.generate_image_v2(prompt, model_name=self.default_model)

    async def generate_image_v2(self, prompt: str, model_name: str = "core") -> Optional[str]:
        if model_name not in self.available_models:
            raise TypeError(f"Model {model_name} is not available")
        url = f"{self.api_host_v2}/stable-image/generate/{model_name}"
        try:
            data = {
                "prompt": prompt,
                "output_format": "jpeg" if model_name == "sd3" else "webp",
            }
            files = {"none": ("dummy.txt", "")}
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers_v2,
                    data=data,
                    files=files,
                )
                if response.status_code == 200:
                    content = await response.aread()
                    return base64.b64encode(content).decode('utf-8')
                raw_text = await response.aread()
                logger.error(f"Error response: {raw_text}")
                raise Exception(f"HTTP {response.status_code}: {raw_text}")
        except Exception as e:
            logger.error(f"An error occurred when generating image: {str(e)}")
            raise Exception(str(e))

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
    prompt = "in the style of ck-mgs, nistyle, Special Ink-drawing mode, intricate linework with expressive contrasts, Mh1$AgThS2, Inkplash art on rice paper, sepia, henna , Silhouette Art, magnificent, inksplash image of stunning japanese woman, gold and red cheongsam, sitting in front of tori gate, facing viewer, dappled sunlight"
    stability_ai_api.default_model = "core"
    base64_image = await stability_ai_api.generate_image(prompt=prompt)

    if base64_image:
        with open("generated_image6.png", "wb") as f:
            f.write(base64.b64decode(base64_image))
        print("Image generated successfully!")
    else:
        print("Failed to generate image")


# Run the example
if __name__ == "__main__":
    asyncio.run(main())

