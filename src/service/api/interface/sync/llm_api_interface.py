from abc import ABC, abstractmethod

class LLMAPIInterface(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    def generate_text_response(self, context: list[object]) -> str:
        pass
