import base64
from abc import ABC, abstractmethod

class Image2TextAPIInterface(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    def describe_image(self, context: list[object], image_b64: str) -> str:
        pass