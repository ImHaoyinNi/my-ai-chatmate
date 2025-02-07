import io
from enum import Enum


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"

class Message:
    def __init__(self, message_type: MessageType, content: str | io.BytesIO):
        self.message_type: MessageType = message_type
        self.content: str | io.BytesIO = content