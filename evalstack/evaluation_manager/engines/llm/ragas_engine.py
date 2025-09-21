
# Import library
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

# Import files
from ..base_engine import EvaluatingEngine
from ..engines_registry import register_engine
from ...metrics.metrics_registry import get_metrics_for_engine
from ....utils.logging_utils import setup_logging

logger = setup_logging("ragas_engine", log_file="logs/evaluation_manager.log")


@register_engine
class RAGASEngine(EvaluatingEngine):
    name = "ragas"

    def evaluate(self, sample: dict) -> dict:
        logger.info(f"Start ragas evaluation.")
        logger.debug("Available metrics for engine %s", get_metrics_for_engine(self.name))

        scores = {}

        for metric in get_metrics_for_engine(self.name):
            if metric.requires_ground_truth and not sample.get("ground_truth"):
                scores[metric.name] = None
                continue
        
            else:
                try:
                    score = metric.evaluate(sample)
                    scores[metric.name] = score
                except Exception as e:
                    scores[metric.name] = f"error: {str(e)}"
                    logger.exception("Metric %s failed", metric.name)

            logger.info(f"Metric scores: {scores}")
    
        return {
            "engine": self.name,
            "scores": scores,
            "meta": {"version": "v_130825"}
        }
        
        #scores = run_metrics_for_engine(sample, engine_name=self.name)

        