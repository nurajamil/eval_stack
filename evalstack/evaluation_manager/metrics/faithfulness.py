import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from .base_metric import EvaluationMetric
from .metrics_registry import register_metric


from ...utils.logging_utils import setup_logging

logger = setup_logging("faithfulness", log_file="logs/evaluation_manager.log")

@register_metric
class FaithfulnessMetric(EvaluationMetric):
    """
    Is the model answer consistent with the provided context (no hallucinations)?
    """

    name = "faithfulness"
    supported_engines = {"ragas"}

    def preprocess(self, sample):

        input = {
            "context": "\n".join(sample.get("context", [])),
            "answer": sample.get("model_answer", ""),
        }
        logger.info(f"Completed preprocessing sample: {input}")

        return input
    
    def build_prompt(self, processed):
        
        prompt = f"""

        Context: 
        {processed["context"]}

        Model Answer: 
        {processed["answer"]}
        
        Is the model's answer factually consistent with ONLY the provided context and 
        ONLY introduce supported facts based on the context? 
        Answer "Yes" or "No".

        """.strip()

        logger.info(f"Completed building prompt.")

        return prompt
    
    
        