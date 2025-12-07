"""
Ollama Client Implementation

This module provides the Ollama local model client.
"""

import json
import requests
from typing import List, Dict, Optional, Iterator

from .base import AIClient


class OllamaClient(AIClient):
    """Ollama local model client."""
    
    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
        timeout: int = 60
    ):
        """
        Initialize the Ollama client.
        
        Args:
            model_name: Name of the Ollama model to use (e.g., "llama3", "mistral").
            base_url: Base URL of the Ollama API server.
            timeout: Request timeout in seconds.
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_url = f"{self.base_url}/api"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat request to Ollama.
        
        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters.
        
        Returns:
            Generated text response.
        
        Raises:
            RuntimeError: If the API call fails.
        """
        # Convert messages to Ollama format
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        
        # Merge any additional options from kwargs
        if "options" in kwargs:
            payload["options"].update(kwargs["options"])
            del kwargs["options"]
        payload.update(kwargs)
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API request failed: {e}") from e
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Send a streaming chat request to Ollama.
        
        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters.
        
        Yields:
            Text chunks as they are generated.
        
        Raises:
            RuntimeError: If the API call fails.
        """
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        
        if "options" in kwargs:
            payload["options"].update(kwargs["options"])
            del kwargs["options"]
        payload.update(kwargs)
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama streaming API request failed: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if Ollama is available and the model is accessible.
        
        Returns:
            True if Ollama is available, False otherwise.
        """
        try:
            # Check if Ollama API is reachable
            response = requests.get(
                f"{self.api_url}/tags",
                timeout=5
            )
            if not response.ok:
                return False
            
            # Check if the model is available
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            return self.model_name in model_names or any(
                self.model_name in name for name in model_names
            )
        except Exception:
            return False
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert message list to a single prompt string for Ollama.
        
        Ollama's generate API uses a single prompt string, so we need to
        convert the message format.
        
        Args:
            messages: List of message dictionaries.
        
        Returns:
            Combined prompt string.
        """
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        # Add final prompt instruction
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

