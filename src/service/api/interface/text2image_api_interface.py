from abc import ABC, abstractmethod

class Text2ImageAPIInterfaceAsync(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    async def generate_image(self, prompt) -> str:
        pass