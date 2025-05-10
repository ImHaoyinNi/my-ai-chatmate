import asyncio
import base64

import httpx

from src.api.interface.text2image_api_interface import Text2ImageAPIInterfaceAsync
from src.utils.logger import logger


class LocalImageGeneratorAPI(Text2ImageAPIInterfaceAsync):
    def __init__(self):
        self.api_host = "http://localhost:8000"

    @property
    def api_name(self) -> str:
        return "local_image_generator"

    async def generate_image(self, prompt) -> str:
        url = f"{self.api_host}/generate"
        try:
            payload = {
                "pos_prompt": prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.0,
                "height": 1024,
                "width": 1024,
                "loras": [{"name": "MoriiMee_Gothic_Niji_Style__Pony_LoRA.safetensors", "scale": 1},]
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data["image_base64"]
                else:
                    logger.error(f"Error response: {response.text}")
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"An error occurred when generating image: {str(e)}")
            raise Exception(str(e))

local_image_generator_api = LocalImageGeneratorAPI()

async def main():
    prompt = "1girl, black hair, black eyes, cleavage, sexy pose, naked, nipples, looking at viewer"
    local_image_generator_api.default_model = "core"
    base64_image = await local_image_generator_api.generate_image(prompt=prompt)

    if base64_image:
        with open("generated_image6.png", "wb") as f:
            f.write(base64.b64decode(base64_image))
        print("Image generated successfully!")
    else:
        print("Failed to generate image")


# Run the example
if __name__ == "__main__":
    asyncio.run(main())
