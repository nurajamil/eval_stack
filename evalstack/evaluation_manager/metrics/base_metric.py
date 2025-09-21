# Import library
from abc import ABC, abstractmethod
from openai import AzureOpenAI
import re
import os
import sys
from typing import Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

# Import files
from common.logger_utils import setup_logger

logger = setup_logger("base-metric", log_file="logs/evaluation_manager.log")

class EvaluationMetric(ABC):
    name: str = None
    requires_ground_truth: bool = False
    # Declare which engines this metric belongs to eg. {"ragas"} or {"ragas", "llm_judging"}
    supported_engines: Set[str] = set()
    
    @abstractmethod
    def preprocess(self, sample: dict) -> dict:
        """
        Extract and prepare inputs for the prompt.
        """

        raise NotImplementedError("Subclasses must implement preprocess.")
    
    @abstractmethod
    def build_prompt(self, processed: dict) -> str:
        """
        Construct the LLM prompt.
        """

        raise NotImplementedError("Subclasses must implement build_prompt.")
    
    def format_input(self, prompt: str) -> list:
        """
        Format the prompt for LLM.
        """
        input = [{
            "role": "user", 
            "content": [{"type": "text", "text": f"{prompt}"}]
            }]
        
        return input

    def call_model(self, prompt: str) -> str:
        """
        Send prompt to model. Can be overridden.
        """
        
        client = AzureOpenAI(
            api_key = "687c8c9647fc49208c8536ba8a00a6b1",  
            api_version = "2025-01-01-preview",
            azure_endpoint = "https://ai-atlas-eastus2.openai.azure.com/openai/deployments/gpt-4.1-atlas/chat/completions?api-version=2025-01-01-preview"
        )

        completion = client.chat.completions.create(
            model="gpt-4.1", 
            messages=prompt,
            temperature=0.0, 
            top_p=0.2,
            max_tokens=4,
            frequency_penalty = 0,
            presence_penalty = 0,
        )

        logger.info(f"Metric model call complete.")

        return completion


    def postprocess(self, result_obj: str) -> float | int:
        """
        Parse model response to a score 0 or 1.
        """
        output_text = result_obj.choices[0].message.content
        if re.match(r"^yes[\s\.,:;!?]*", output_text.strip(), flags=re.IGNORECASE):
            logger.debug("Detected leading 'yes' -> score = 1")
            score = 1 
        else:
            logger.debug("No leading 'yes' -> score = 0")
            score = 0

        logger.info(f"Metric postprocess -> {score} | raw: {output_text!r}")

        return score

    
    def evaluate(self, sample: dict) -> float | int:
        """
        Evaluate a single sample. Must return a numeric score (0 or 1).
        """

        processed = self.preprocess(sample)
        prompt = self.build_prompt(processed)
        input = self.format_input(prompt)
        result_obj = self.call_model(input)
        output_text = self.postprocess(result_obj)

        logger.info(f"Completed evaluation for sample.")

        return output_text

