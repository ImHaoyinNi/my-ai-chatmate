import io
from abc import ABC, abstractmethod

from src.constants import Speaker


class VoiceAPIInterface(ABC):
    @abstractmethod
    def transcribe(self, voice_buffer: io.BytesIO) -> str:
        pass

    @abstractmethod
    def text2audio(self, text, speaker: Speaker=Speaker.WOMAN) -> io.BytesIO:
        pass