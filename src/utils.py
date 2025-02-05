import base64
import io
import re
from langdetect import detect
from PIL import Image
from promptgen import generate_prompts

from src.service.persona import get_persona_prompt


def remove_think_tag(text: str):
    return re.sub(r'(?s)<think>.*?</think>', '', text).strip()

def english_or_chinese(text: str):
    return detect(text)

def parse_idle_time(idle_time: str) -> int:
    """Parses a string like '2h', '30m', '1d' into seconds."""
    match = re.match(r"(\d+)([hm])", idle_time.strip().lower())
    if not match:
        raise ValueError("Invalid idle_time format. Use 'Xm' for minutes or 'Xh' for hours.")

    value, unit = int(match.group(1)), match.group(2)
    if unit == "h":
        return value * 3600
    elif unit == "m":
        return value * 60
    return 0

def save_base64_as_png(base64_string, output_filename="./output.png"):
    """Converts a base64 string to a PNG image and saves it."""
    image_data = base64.b64decode(base64_string)  # Decode base64
    with open(output_filename, "wb") as f:
        f.write(image_data)  # Save as PNG file
    print(f"Image saved as {output_filename}")

def generate_image_prompt(text):
    detailed_prompt = generate_prompts(text)
    return detailed_prompt

def compress_base64_image(image_b64, max_size=5 * 1024 * 1024, quality=90):
    """Compresses a base64-encoded image to ensure it does not exceed max_size.
    Args:
        image_b64 (str): The input base64-encoded image string.
        max_size (int, optional): Maximum allowed file size in bytes. Defaults to 5MB.
        quality (int, optional): Starting quality for JPEG compression. Defaults to 90.

    Returns:
        str: The compressed image as a base64-encoded string.
    """
    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data))
    img_format = "JPEG" if image.format == "PNG" else image.format  # Convert PNG to JPEG for better compression

    while True:
        buffer = io.BytesIO()
        image.save(buffer, format=img_format, quality=quality)
        size = buffer.tell()
        if size <= max_size or quality <= 10:
            break
        quality -= 5

    compressed_b64 = base64.b64encode(buffer.getvalue()).decode()
    return compressed_b64

if __name__ == "__main__":
    context = [{"role": "system", "content": get_persona_prompt("chick")},
               {"role": "user", "content": "What are you doing?"},
               {"role": "assistant", "content": "Drinking a coffee"},]
    res = generate_image_prompt(str(context))
    print(res)