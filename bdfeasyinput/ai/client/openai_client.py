"""
OpenAI Client Implementation

This module provides the OpenAI API client.
"""

import os
from typing import List, Dict, Optional, Iterator

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from .base import AIClient


class OpenAIClient(AIClient):
    """OpenAI API client."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo").
            api_key: OpenAI API key. If not provided, will try to get from environment.
            base_url: Custom API base URL (for OpenAI-compatible APIs).
            timeout: Request timeout in seconds.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. "
                "Install it with: pip install openai>=1.0.0"
            )
        
        self.model = model
        self.timeout = timeout
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        client_kwargs = {"api_key": api_key, "timeout": timeout}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat request to OpenAI.
        
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
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}") from e
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Send a streaming chat request to OpenAI.
        
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
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            raise RuntimeError(f"OpenAI streaming API request failed: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if OpenAI client is available and configured.
        
        Returns:
            True if the client is ready, False otherwise.
        """
        if not OPENAI_AVAILABLE:
            return False
        
        try:
            # Simple check: try to list models (lightweight operation)
            # For now, just check if API key is set
            api_key = os.getenv("OPENAI_API_KEY")
            return api_key is not None and len(api_key) > 0
        except Exception:
            return False

