import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from .base_metric import EvaluationMetric
from .metrics_registry import register_metric

from ...utils.logging_utils import setup_logging

logger = setup_logging("accuracy", log_file="logs/evaluation_manager.log")

@register_metric
class AccuracyMetric(EvaluationMetric):
    """
    - How closely the model answer matches the ground truth
    - Measures whether the model_answer matches the known ground_truth for the question.
    """

    name = "accuracy"
    requires_ground_truth = True
    supported_engines = {"ragas"}

    def preprocess(self, sample):

        input = {
            "question": sample.get("processed_user_query") 
                        or sample.get("original_user_query")
                        or "",
            "answer": sample.get("model_answer", ""),
            "ground_truth": sample.get("ground_truth", "")
        }
        logger.info(f"Preprocessing accuracy input: {input}")

        return input
    
    def build_prompt(self, processed):
        
        prompt = f"""

        Question:
        {processed["question"]}

        Model Answer:
        {processed["answer"]}

        Ground Truth:
        {processed["ground_truth"]}

        Does the model's answer correctly match the ground-truth answer for the question? 
        Evaluate based on factual accuracy and completeness. Ignore differences in style or phrasing. 
        Answer "Yes" or "No".

        """.strip()

        logger.info(f"Completed building prompt.")

        return prompt
        
