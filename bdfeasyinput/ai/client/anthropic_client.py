"""
Anthropic Claude Client Implementation

This module provides the Anthropic Claude API client.
"""

import os
from typing import List, Dict, Optional, Iterator

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

from .base import AIClient


class AnthropicClient(AIClient):
    """Anthropic Claude API client."""
    
    def __init__(
        self,
        model: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize the Anthropic client.
        
        Args:
            model: Model name (e.g., "claude-3-opus-20240229", "claude-3-sonnet-20240229").
            api_key: Anthropic API key. If not provided, will try to get from environment.
            timeout: Request timeout in seconds.
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package is not installed. "
                "Install it with: pip install anthropic>=0.3.0"
            )
        
        self.model = model
        self.timeout = timeout
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key is required. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )
        
        self.client = Anthropic(api_key=api_key, timeout=timeout)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat request to Anthropic.
        
        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate (default 4096 for Claude).
            **kwargs: Additional parameters.
        
        Returns:
            Generated text response.
        
        Raises:
            RuntimeError: If the API call fails.
        """
        # Anthropic requires max_tokens to be set
        if max_tokens is None:
            max_tokens = 4096
        
        # Convert messages format for Anthropic
        # Anthropic expects system message separately and user/assistant messages
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                if system_message is None:
                    system_message = content
                else:
                    system_message += "\n" + content
            elif role in ["user", "assistant"]:
                conversation_messages.append({
                    "role": role,
                    "content": content
                })
        
        try:
            call_kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": conversation_messages,
                **kwargs
            }
            
            if system_message:
                call_kwargs["system"] = system_message
            
            response = self.client.messages.create(**call_kwargs)
            
            # Extract text content from response
            text_content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    text_content += content_block.text
            
            return text_content
        except Exception as e:
            raise RuntimeError(f"Anthropic API request failed: {e}") from e
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Send a streaming chat request to Anthropic.
        
        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate (default 4096).
            **kwargs: Additional parameters.
        
        Yields:
            Text chunks as they are generated.
        
        Raises:
            RuntimeError: If the API call fails.
        """
        if max_tokens is None:
            max_tokens = 4096
        
        # Convert messages format
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                if system_message is None:
                    system_message = content
                else:
                    system_message += "\n" + content
            elif role in ["user", "assistant"]:
                conversation_messages.append({
                    "role": role,
                    "content": content
                })
        
        try:
            call_kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": conversation_messages,
                "stream": True,
                **kwargs
            }
            
            if system_message:
                call_kwargs["system"] = system_message
            
            with self.client.messages.stream(**call_kwargs) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        if event.delta.type == "text":
                            yield event.delta.text
        except Exception as e:
            raise RuntimeError(f"Anthropic streaming API request failed: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if Anthropic client is available and configured.
        
        Returns:
            True if the client is ready, False otherwise.
        """
        if not ANTHROPIC_AVAILABLE:
            return False
        
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            return api_key is not None and len(api_key) > 0
        except Exception:
            return False

