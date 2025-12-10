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

try:
    from .openrouter_client import OpenRouterClient  # noqa: F401
except ImportError:
    OpenRouterClient = None

try:
    from .openai_compatible import (
        create_openai_compatible_client,
        get_available_services,
        get_service_config,
        SERVICE_CONFIGS,
    )  # noqa: F401
except ImportError:
    create_openai_compatible_client = None
    get_available_services = None
    get_service_config = None
    SERVICE_CONFIGS = None

__all__ = [
    'AIClient',
    'OllamaClient',
    'OpenAIClient',
    'AnthropicClient',
    'OpenRouterClient',
    'create_openai_compatible_client',
    'get_available_services',
    'get_service_config',
    'SERVICE_CONFIGS',
]

