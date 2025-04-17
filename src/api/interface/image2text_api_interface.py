from abc import ABC, abstractmethod

class Image2TextAPIInterfaceAsync(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    async def describe_image(self, context: list[object], image_b64: str) -> str:
        pass