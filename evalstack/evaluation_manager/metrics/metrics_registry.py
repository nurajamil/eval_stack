# Import library
import os
import sys
from typing import List, Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

# Import files
from common.logger_utils import setup_logger
from .base_metric import EvaluationMetric

logger = setup_logger("metrics_registry", log_file="logs/evaluation_manager.log")

_METRICS_REGISTRY: List[EvaluationMetric] = []


def register_metric(cls):
    """
    Decorator to register a metric.
    """
    logger.debug(f"Registering metric: {cls.__name__}")

    inst = cls()
    _METRICS_REGISTRY.append(inst)
    
    return cls
    #logger.debug(f"Registering metric: {cls.__name__}")
    #if not cls.name:
    #    raise ValueError("Metric class must define a unique 'name'.")
    
    #_METRICS_REGISTRY[cls.name] = cls()

    #logger.debug(f"Completed Registering: {_METRICS_REGISTRY}")
    #return cls

def get_metric(name):
    return _METRICS_REGISTRY[name]

def get_all_metrics():
    logger.debug(f"Current metrics in registry: {list(_METRICS_REGISTRY.keys())}")

    return _METRICS_REGISTRY.values()

def get_metrics_for_engine(engine_name: str) -> List[EvaluationMetric]:
    return [m for m in _METRICS_REGISTRY if (not m.supported_engines) or (engine_name in m.supported_engines)]


