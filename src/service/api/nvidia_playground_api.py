import base64
import io
import os

import requests
from openai import OpenAI

from src.service.api.interface.image2text_api_interface import Image2TextAPIInterface
from src.service.api.interface.llm_api_interface import LLMAPIInterface
from dotenv import load_dotenv

from src.service.api.interface.text2image_api_interface import Text2ImageAPIInterface
from src.service.api.interface.tts_api_interface import TTSAPIInterface
from src.utils import compress_base64_image, save_base64_as_png


class NvidiaPlaygroundAPI(LLMAPIInterface, Image2TextAPIInterface, Text2ImageAPIInterface):
    @property
    def api_name(self):
        return "Nvidia Playground API"

    def __init__(self,
                 api_url="https://integrate.api.nvidia.com/v1",
                 text_model="deepseek-ai/deepseek-r1",
                 image2text_api_url="https://ai.api.nvidia.com/v1/gr/meta/llama-3.2-90b-vision-instruct/chat/completions",
                 text2image_api_url="https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl"
                 ):
        self._text_model = text_model
        self._api_url = api_url
        self._api_name = "nvidia playground"
        load_dotenv()
        self._api_key = os.getenv("NVIDIA_API_KEY")
        self.client = OpenAI(
            base_url=self._api_url,
            api_key=self._api_key
        )

        self._image2text_api_url = image2text_api_url
        self._text2image_api_url = text2image_api_url

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

    def text_to_image(self, text: str) -> str:
        return ""

    def describe_image(self, context: list[dict], image_b64: str) -> str:
        if len(image_b64) > 180000:
            image_b64 = compress_base64_image(image_b64)
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json"
        }
        payload = {
            "model": 'meta/llama-3.2-90b-vision-instruct',
            "messages": [
                {
                    "role": "user",
                    "content": f'What is in this image? <img src="data:image/png;base64,{image_b64}" />'
                }
            ],
            "max_tokens": 512,
            "temperature": 1.00,
            "top_p": 1.00,
            "stream": False
        }
        response = requests.post(self._image2text_api_url, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]

    def generate_image(self, pos: str, neg: str="") -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        payload = {
            "text_prompts": [{"text": pos,"weight": 1},
                             {"text": neg,"weight": -1}],
            "cfg_scale": 5,
            "sampler": "K_DPM_2_ANCESTRAL",
            "seed": 0,
            "steps": 25
        }

        response = requests.post(self._text2image_api_url, headers=headers, json=payload)
        response.raise_for_status()
        response_body = response.json()
        return response_body["artifacts"][0]["base64"]

    def generate_image_consistory(self, subject_prompt, scene_prompt1, scene_prompt2, neg_prompt="", style_prompt="A photo of") -> str:
        invoke_url = "https://ai.api.nvidia.com/v1/genai/nvidia/consistory"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
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
        response = requests.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        for idx, img_data in enumerate(data['artifacts']):
            img_base64 = img_data["base64"]
        return img_base64

nvdia_playground_api = NvidiaPlaygroundAPI()

if __name__ == '__main__':
    with open("./9.JPG", "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    # des = nvdia_playground_api.describe_image(context=[], image_b64=image_b64)
    pos = "Kim Jong Un reading a newspaper, newspaper says the nuclear war with USA is coming"
    img64 = nvdia_playground_api.generate_image_consistory(pos)
    save_base64_as_png(img64)