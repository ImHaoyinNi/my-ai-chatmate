from abc import ABC, abstractmethod

class LLMAPIInterfaceAsync(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    async def generate_text_response(self, context: list[dict]) -> str:
        pass
