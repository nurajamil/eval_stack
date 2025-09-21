
# Import library
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

# Import files
from ...utils.logging_utils import setup_logging

logger = setup_logging("engines_registry", log_file="logs/evaluation_manager.log")

_ENGINES_REGISTRY = {}

def register_engine(cls):
    logger.debug(f"Registering evaluating engine: {cls.__name__}")
    _ENGINES_REGISTRY[cls.name] = cls()

    logger.debug(f"Completed registering: {_ENGINES_REGISTRY.keys()}")
    return cls

def get_all_engines():
    logger.debug(f"Current engines in registry: {list(_ENGINES_REGISTRY.keys())}")
    return list(_ENGINES_REGISTRY.values())

def get_engine(name: str):
    return _ENGINES_REGISTRY.get(name)