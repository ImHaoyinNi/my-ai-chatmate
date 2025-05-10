import base64
import datetime
import io
import random
import re
from asyncio import sleep

import pytz
from langdetect import detect
from PIL import Image
from promptgen import generate_prompts
from telegram.constants import ChatAction, ParseMode

from src.data.Message import Message, MessageType

async def send_message(bot, user_id: int, message: Message):
    match message.message_type:
        case MessageType.TEXT:
            if message.content.startswith('"') and message.content.endswith('"'):
                message.content = message.content[1:-1]
            sentences = split_message_randomly(message.content)
            for s in sentences:
                await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
                await sleep(delay=time_to_type(s))
                await bot.send_message(chat_id=user_id, text=s)
        case MessageType.VOICE:
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
            await sleep(delay=time_to_type(message.content))
            await bot.send_voice(chat_id=user_id, voice=message.content)
        case MessageType.IMAGE:
            await bot.send_photo(
                chat_id=user_id,
                photo=message.content,
                # TODO: Add caption later
                caption=None,
                parse_mode=ParseMode.HTML
            )
        case MessageType.BAD_MESSAGE:
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
            await bot.send_message(chat_id=user_id, text=message.content)
        case MessageType.NONE:
            return

def get_image_prompt(message: str) -> str:
    start_tag = "<image_prompt>"
    end_tag = "</image_prompt>"
    start_idx = message.find(start_tag)
    end_idx = message.find(end_tag)
    if start_idx != -1 and end_idx != -1:
        prompt_start = start_idx + len(start_tag)
        return message[prompt_start:end_idx]
    return ""

def remove_image_prompt(message: str) -> str:
    start_tag = "<image_prompt>"
    end_tag = "</image_prompt>"
    start_idx = message.find(start_tag)
    end_idx = message.find(end_tag)
    if start_idx != -1 and end_idx != -1:
        return message[:start_idx].strip() + " " + message[end_idx + len(end_tag):].strip()
    return message

def remove_think_tag(text: str):
    # return re.sub(r'(?s)<think>.*?</think>', '', text).strip()
    return re.sub(r'(?s)^.*?</think>', '', text).strip()

def remove_quotes(text: str) -> str:
    if text.startswith('"'):
        text = text[1:]
    if text.endswith('"'):
        text = text[:-1]
    return text

def get_current_time(timezone="America/Chicago") -> (int, int):
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)  # Get the current time once
    return now.hour, now.minute

def split_message_randomly(text: str, min_group_size: int=1, max_group_size: int=3) -> list[str]:
    sentences = []
    current_sentence = ""

    # First split by obvious sentence boundaries
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    for part in parts:
        sentences.append(part)

    # Extract emojis at the end of the last sentence
    last_sentence = sentences[-1]
    emoji_pattern = r'[\U0001F000-\U0001F9FF]+$'
    emoji_match = re.search(emoji_pattern, last_sentence)

    if emoji_match:
        # Remove emojis from last sentence and add as separate item
        emojis = emoji_match.group()
        sentences[-1] = last_sentence[:emoji_match.start()]
        sentences.append(emojis)

    # Create random groupings
    result = []
    i = 0
    while i < len(sentences):
        # Determine random group size within bounds
        remaining = len(sentences) - i
        max_possible = min(max_group_size, remaining)
        group_size = random.randint(min_group_size, max_possible)

        # Get the group of sentences
        group = sentences[i:i + group_size]
        result.append(' '.join(group).strip())

        i += group_size

    return result


def time_to_type(content: str | io.BytesIO) -> float:
    if isinstance(content, str):
        delay = 1 + (len(content) / 100) * 4
    else:
        content.seek(0, io.SEEK_END)
        size_bytes = content.tell()
        content.seek(0)  # Reset position
        delay = 1 + (size_bytes / 10240)  # 10KB ≈ 1 second
    delay = min(5.0, max(1.0, delay))
    actual_delay = random.uniform(delay * 0.8, delay * 1.2)
    return actual_delay

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
    # context = [{"role": "system", "content": get_persona_prompt("chick")},
    #            {"role": "user", "content": "What are you doing?"},
    #            {"role": "assistant", "content": "Drinking a coffee"},]
    # res = generate_image_prompt(str(context))
    # print(res)
    msg = "Hey love! just finished baseball practice and my arm’s kinda dead. You free tonight? I saved you a slice of that lemon tart I baked earlier 😉"
    res = split_message_randomly(msg)
    print(len(res))
    print(res)