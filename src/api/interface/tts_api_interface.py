import io
from abc import ABC, abstractmethod

class TTSAPIInterface(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, voice_id: str) -> io.BytesIO:
        pass