"""
OpenAI-Compatible Client Factory

This module provides a factory function to create OpenAI-compatible clients
for various services like OpenRouter, Together AI, etc.
"""

import os
from typing import Optional, Dict, Any

from .openai_client import OpenAIClient, OPENAI_AVAILABLE


# Predefined service configurations
SERVICE_CONFIGS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_model": "openai/gpt-4",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "api_key_env": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Llama-2-70b-chat-hf",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "default_model": "llama-3-70b-8192",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "api_key_env": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
    },
    "perplexity": {
        "base_url": "https://api.perplexity.ai",
        "api_key_env": "PERPLEXITY_API_KEY",
        "default_model": "pplx-70b-online",
    },
}


def create_openai_compatible_client(
    service: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 60
) -> OpenAIClient:
    """
    Create an OpenAI-compatible client for a specific service.
    
    Args:
        service: Service name (e.g., "openrouter", "together", "groq").
        model: Model name. If not provided, uses service default.
        api_key: API key. If not provided, tries to get from environment.
        base_url: Custom base URL. If not provided, uses service default.
        timeout: Request timeout in seconds.
    
    Returns:
        Configured OpenAIClient instance.
    
    Raises:
        ValueError: If service is not supported or API key is missing.
        ImportError: If OpenAI package is not installed.
    
    Examples:
        >>> # OpenRouter
        >>> client = create_openai_compatible_client("openrouter", model="openai/gpt-4")
        
        >>> # Together AI
        >>> client = create_openai_compatible_client("together", model="meta-llama/Llama-2-70b-chat-hf")
        
        >>> # Custom service
        >>> client = create_openai_compatible_client(
        ...     "custom",
        ...     model="custom-model",
        ...     base_url="https://api.custom.com/v1",
        ...     api_key="custom-key"
        ... )
    """
    if not OPENAI_AVAILABLE:
        raise ImportError(
            "OpenAI package is not installed. "
            "Install it with: pip install openai>=1.0.0"
        )
    
    # Get service configuration
    if service.lower() in SERVICE_CONFIGS:
        config = SERVICE_CONFIGS[service.lower()]
        default_base_url = config["base_url"]
        default_api_key_env = config["api_key_env"]
        default_model = config.get("default_model")
    else:
        # Custom service - require base_url and api_key
        default_base_url = base_url
        default_api_key_env = None
        default_model = model
    
    # Determine base URL
    final_base_url = base_url or default_base_url
    if not final_base_url:
        raise ValueError(
            f"Service '{service}' is not supported and no base_url provided. "
            f"Supported services: {', '.join(SERVICE_CONFIGS.keys())}"
        )
    
    # Get API key
    if api_key:
        final_api_key = api_key
    elif default_api_key_env:
        final_api_key = os.getenv(default_api_key_env)
    else:
        # Try common environment variable names
        final_api_key = (
            os.getenv(f"{service.upper()}_API_KEY") or
            os.getenv("OPENAI_API_KEY")
        )
    
    if not final_api_key:
        env_var = default_api_key_env or f"{service.upper()}_API_KEY"
        raise ValueError(
            f"API key is required for service '{service}'. "
            f"Set {env_var} environment variable or pass api_key parameter."
        )
    
    # Determine model
    final_model = model or default_model or "gpt-4"
    
    # Create and return client
    return OpenAIClient(
        model=final_model,
        api_key=final_api_key,
        base_url=final_base_url,
        timeout=timeout
    )


def get_available_services() -> list:
    """
    Get list of available service names.
    
    Returns:
        List of service names.
    """
    return list(SERVICE_CONFIGS.keys())


def get_service_config(service: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific service.
    
    Args:
        service: Service name.
    
    Returns:
        Service configuration dictionary, or None if not found.
    """
    return SERVICE_CONFIGS.get(service.lower())

