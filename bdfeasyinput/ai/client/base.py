"""
Base AI Client Interface

This module defines the abstract base class for all AI clients.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Iterator, Any


class AIClient(ABC):
    """Base interface for AI clients."""
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat request and return the response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
                     Roles can be 'system', 'user', or 'assistant'.
            temperature: Sampling temperature (0.0-2.0). Higher values make output more random.
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional provider-specific parameters.
        
        Returns:
            The generated text response.
        
        Raises:
            RuntimeError: If the API call fails.
        """
        pass
    
    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Send a streaming chat request and return an iterator of response chunks.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional provider-specific parameters.
        
        Yields:
            Text chunks as they are generated.
        
        Raises:
            RuntimeError: If the API call fails.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI client is available and configured correctly.
        
        Returns:
            True if the client is ready to use, False otherwise.
        """
        pass

