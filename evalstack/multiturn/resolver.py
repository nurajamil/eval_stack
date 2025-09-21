# Import libraries
from abc import ABC, abstractmethod
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Import files
from ..types import Turn

class QueryProcessor():
    def __init__(self, block):
        self.api_key = os.getenv("OPENAI_GPT5_API_KEY")
        self.model = "gpt-5-mini"

    
    def format_input(self, block):
        messages = [{
            "role": "user", 
            "content": [{"type": "text", "text": f"{block}"}]
        }]
        return messages
    
    def initialize_client(self):
        client = OpenAI(
            api_key=self.api_key
        ) 
        return client

        client = openai(
            api_key = os.
        )


    @abstractmethod
    def process_block(self, block: str, history: List[Turn]) -> str:
        pass