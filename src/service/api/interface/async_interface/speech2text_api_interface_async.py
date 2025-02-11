import io
from abc import ABC, abstractmethod

class Speech2TextAPIInterfaceAsync(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    async def speech_to_text(self, speech: io.BytesIO) -> str:
        pass