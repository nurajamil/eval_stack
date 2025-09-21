from abc import ABC, abstractmethod
from typing import Dict, Any

class EvaluatingEngine(ABC):
    """
    Runs one evaluation framework on a single sample.
    """

    name: str

    @abstractmethod
    def evaluate(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a dict of scores and metadata.
        Example:
        {
            "engine": "ragas",
            "scores": {"accuracy": 1, "faithfulness": 0, ...},
            "meta": {"notes": "..",..}        
        }
        """

        raise NotImplementedError("Subclasses must implement evaluate.")