import asyncio
import aiohttp
import base64

from src.service.api.interface.text2image_api_interface import Text2ImageAPIInterfaceAsync
from src.utils.config import config
from src.utils.logger import logger


class AIHordeGenerator(Text2ImageAPIInterfaceAsync):
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.api_url = "https://stablehorde.net/api/v2"
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        self.model=config.ai_horde_api_settings["model_name"],
        self.return_base64=False
        self.nsfw = config.ai_horde_api_settings["nsfw"]

    @property
    def api_name(self) -> str:
        return "AI Horde API"

    async def generate_image(self, prompt) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "prompt": prompt,
                "models": self.model,
                "params": {
                    "sampler_name": "k_euler",
                    "cfg_scale": 6.0,
                    "steps": 30,
                    "width": 512,
                    "height": 512,
                },
                "nsfw": self.nsfw,
                "trusted_workers": True,
                "censor_nsfw": False if self.nsfw else True,
            }

            # Submit request
            async with session.post(
                    f"{self.api_url}/generate/async",
                    headers=self.headers,
                    json=payload
            ) as response:
                response_json = await response.json()
                if 'errors' in response_json:
                    raise Exception(f"Error submitting request: {response_json}")
                request_id = response_json["id"]
                logger.info(f"Request submitted successfully. Kudos: {response_json.get('kudos', 'unknown')}")

            # Wait for completion
            while True:
                async with session.get(
                        f"{self.api_url}/generate/check/{request_id}"
                ) as check_response:
                    if check_response.status != 200:
                        raise Exception(f"Error checking status: {await check_response.text()}")

                    status = await check_response.json()
                    if status["done"]:
                        break
                    print(status)
                    await asyncio.sleep(4)

            # Get result
            async with session.get(
                    f"{self.api_url}/generate/status/{request_id}"
            ) as result_response:
                if result_response.status != 200:
                    raise Exception(f"Error getting result: {await result_response.text()}")

                generations = (await result_response.json())["generations"]
                if not generations:
                    raise Exception("No generations returned")

                image_url = generations[0]["img"]

                if self.return_base64:
                    # Download and convert to base64
                    async with session.get(image_url) as img_response:
                        if img_response.status != 200:
                            raise Exception("Failed to download image")

                        img_data = await img_response.read()
                        base64_string = base64.b64encode(img_data).decode('utf-8')
                        return base64_string
                return image_url

ai_horde_api = AIHordeGenerator(config.ai_horde_api_key)
async def main():
    generator = AIHordeGenerator(api_key=config.ai_horde_api_key)  # Empty for anonymous

    prompt = "A sexy woman with D cup is playing baseball. She is a catcher. She sweats heavily"

    try:
        print("Starting image generation...")
        base64_image = await generator.generate_image(prompt)
        print("Generation complete!")
        print(f"Base64 string length: {len(base64_image)}")

        # Optionally save the base64 to a file
        with open("image_base64.txt", "w") as f:
            f.write(base64_image)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())