import io
from abc import ABC, abstractmethod

class TTSAPIInterface(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    def text_to_speech(self, text: str, speaker: str) -> io.BytesIO:
        pass