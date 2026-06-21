import ollama
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OllamaClient:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model = model_name

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Interacts with the local Ollama instance.
        """
        try:
            logging.info(f"Sending request to Ollama ({self.model})...")
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ])
            return response['message']['content']
        except Exception as e:
            logging.error(f"Ollama connection error: {e}")
            raise ConnectionError(f"Failed to connect to Ollama: {str(e)}")

    def is_alive(self) -> bool:
        try:
            ollama.list()
            return True
        except:
            return False
