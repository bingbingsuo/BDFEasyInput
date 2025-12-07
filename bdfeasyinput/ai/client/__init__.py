"""
AI Client Module

This module provides interfaces and implementations for various AI providers.
"""

from .base import AIClient  # noqa: F401

# Optional imports - only import if dependencies are available
try:
    from .ollama import OllamaClient  # noqa: F401
except ImportError:
    OllamaClient = None

try:
    from .openai_client import OpenAIClient  # noqa: F401
except ImportError:
    OpenAIClient = None

try:
    from .anthropic_client import AnthropicClient  # noqa: F401
except ImportError:
    AnthropicClient = None

__all__ = [
    'AIClient',
    'OllamaClient',
    'OpenAIClient',
    'AnthropicClient',
]

