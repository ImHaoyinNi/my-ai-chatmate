import io
from enum import Enum


class ReplyType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"

class Reply:
    def __init__(self, reply_type: ReplyType, content: str | io.BytesIO):
        self.reply_type: ReplyType = reply_type
        self.content: str | io.BytesIO = content