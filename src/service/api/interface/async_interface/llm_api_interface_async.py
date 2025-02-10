from abc import ABC, abstractmethod
from typing import List

class LLMAPIInterfaceAsync(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    async def generate_text_response(self, context: List[object]) -> str:
        pass
