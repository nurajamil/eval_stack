# Import libraries
from abc import ABC, abstractmethod

class SelfContainmentDetector(ABC):
    @abstractmethod
    def is_self_contained(self, query: str) -> bool:
        pass