"""
OpenRouter Client Implementation

OpenRouter is an OpenAI-compatible API service that provides access to multiple
AI models. This client uses the OpenAI client with OpenRouter's base URL.
"""

import os
from typing import List, Dict, Optional, Iterator

from .openai_client import OpenAIClient, OPENAI_AVAILABLE


class OpenRouterClient(OpenAIClient):
    """OpenRouter API client (OpenAI-compatible)."""
    
    # OpenRouter API base URL
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(
        self,
        model: str = "openai/gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize the OpenRouter client.
        
        Args:
            model: Model name (e.g., "openai/gpt-4", "anthropic/claude-3-sonnet").
                   See https://openrouter.ai/models for available models.
            api_key: OpenRouter API key. If not provided, will try to get from environment.
            base_url: Custom API base URL (defaults to OpenRouter's API).
            timeout: Request timeout in seconds.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. "
                "Install it with: pip install openai>=1.0.0"
            )
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )
        
        # Use OpenRouter's base URL by default
        base_url = base_url or self.DEFAULT_BASE_URL
        
        # Initialize parent class with OpenRouter settings
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
        
        # OpenRouter requires additional headers
        # Set default headers for OpenRouter (these are added automatically by OpenAI client)
        if hasattr(self.client, 'default_headers'):
            self.client.default_headers.update({
                "HTTP-Referer": os.getenv("OPENROUTER_REFERER", "https://github.com/BDFEasyInput/BDFEasyInput"),
                "X-Title": os.getenv("OPENROUTER_TITLE", "BDFEasyInput")
            })
    
    def is_available(self) -> bool:
        """
        Check if OpenRouter client is available and configured.
        
        Returns:
            True if the client is ready, False otherwise.
        """
        if not OPENAI_AVAILABLE:
            return False
        
        try:
            # Check for API key in environment (try both OPENROUTER_API_KEY and OPENAI_API_KEY)
            api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
            return api_key is not None and len(api_key) > 0
        except Exception:
            return False
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat request to OpenRouter with required headers.
        
        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters.
        
        Returns:
            Generated text response.
        """
        # Add OpenRouter headers if available
        if hasattr(self, '_default_headers'):
            # Note: OpenAI client doesn't directly support custom headers in chat()
            # We'll need to set them on the client's default_headers
            if hasattr(self.client, 'default_headers'):
                self.client.default_headers.update(self._default_headers)
        
        # Call parent chat method
        return super().chat(messages, temperature, max_tokens, **kwargs)

