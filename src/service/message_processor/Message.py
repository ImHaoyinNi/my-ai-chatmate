import datetime
import io
import json
import base64
from enum import Enum
from dataclasses import dataclass, field
from typing import Union, Optional, Dict

from src.redis.redis_client import redis_client


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    ANY = "any"
    NONE = "none"
    BAD_MESSAGE = "bad_message"


@dataclass
class Message:
    message_type: MessageType
    content: Union[str, io.BytesIO]
    prompt: str
    user_id: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict:
        result = {
            "message_type": self.message_type.value,
            "prompt": self.prompt,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
        }
        if isinstance(self.content, str):
            result["content"] = self.content
            result["content_type"] = "str"
        elif isinstance(self.content, io.BytesIO):
            self.content.seek(0)
            binary_data = self.content.read()
            result["content"] = base64.b64encode(binary_data).decode('utf-8')
            result["content_type"] = "bytes"
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        message_type = MessageType(data["message_type"])
        prompt = data["prompt"]
        user_id = data["user_id"]
        if data["content_type"] == "str":
            content = data["content"]
        elif data["content_type"] == "bytes":
            binary_data = base64.b64decode(data["content"])
            content = io.BytesIO(binary_data)

        return cls(message_type=message_type, content=content, prompt=prompt, user_id=user_id, timestamp=data["timestamp"])


class MessageQueue:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None):
        self.redis_client = redis_client

    def _get_queue_key(self, user_id: int) -> str:
        return f"message_queue:{user_id}"

    def enqueue(self, user_id: int, message: Message) -> None:
        queue_key = self._get_queue_key(user_id)
        message_data = message.to_dict()
        self.redis_client.rpush(queue_key, json.dumps(message_data))

    def dequeue(self, user_id: int) -> Optional[Message]:
        queue_key = self._get_queue_key(user_id)
        message_json = self.redis_client.lpop(queue_key)
        if message_json is None:
            return None
        message_data = json.loads(message_json)
        return Message.from_dict(message_data)

    def get_length(self, user_id: int) -> int:
        queue_key = self._get_queue_key(user_id)
        return self.redis_client.llen(queue_key)


message_queue = MessageQueue()
