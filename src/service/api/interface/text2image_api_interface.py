from abc import ABC, abstractmethod

class Text2ImageAPIInterface(ABC):
    @property
    @abstractmethod
    def api_name(self) -> str:
        pass

    @abstractmethod
    def generate_image(self, pos: str, neg: str) -> str:
        pass