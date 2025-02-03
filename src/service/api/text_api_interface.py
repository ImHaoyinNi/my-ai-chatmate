from abc import ABC, abstractmethod

class TextAPIInterface(ABC):
    @abstractmethod
    def generate_text_response(self, context: list[object]):
        pass
