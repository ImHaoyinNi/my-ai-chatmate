import io
from enum import Enum


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    ANY = "any"
    NONE = "none"
    BAD_MESSAGE = "bad_message"

class Message:
    def __init__(self, message_type: MessageType, content: str | io.BytesIO, prompt: str):
        self.message_type: MessageType = message_type
        self.content: str | io.BytesIO = content
        self.prompt: str = prompt

class MessageQueue:
    def __init__(self):
        self.queue: dict[int, list[Message]] = dict()

    def enqueue(self, user_id: int, message: Message) -> None:
        if user_id not in self.queue:
            self.queue[user_id] = []
        self.queue[user_id].append(message)

    def dequeue(self, user_id: int) -> Message | None:
        if user_id not in self.queue:
            return None
        return self.queue[user_id].pop(0)

    def get_length(self, user_id: int) -> int:
        if user_id not in self.queue:
            return 0
        return len(self.queue[user_id])

message_queue = MessageQueue()
