from enum import Enum

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class Speaker(Enum):
    WOMAN = "v2/en_speaker_9"

def new_message(role: Role, content: str) -> dict:
    message = {
        "role": role.value,
        "content": content
    }
    return message
