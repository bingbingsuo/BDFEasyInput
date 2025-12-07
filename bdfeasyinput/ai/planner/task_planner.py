"""
Task Planner

This module provides the main task planning functionality.
"""

from typing import Dict, Any, Optional, List
import logging

from ..client.base import AIClient
from ..prompt.templates import build_system_prompt, build_user_prompt
from ..parser.response_parser import parse_ai_response, AIResponseParseError
from ...validator import BDFValidator, ValidationError

logger = logging.getLogger(__name__)


class PlanningError(Exception):
    """Error raised when task planning fails."""
    pass


class TaskPlanner:
    """Task planner for generating BDF calculation configurations from natural language."""
    
    def __init__(
        self,
        ai_client: AIClient,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        validate_output: bool = True
    ):
        """
        Initialize the task planner.
        
        Args:
            ai_client: AI client to use for planning.
            temperature: Sampling temperature for AI generation.
            max_tokens: Maximum tokens to generate.
            max_retries: Maximum number of retries if parsing fails.
            validate_output: Whether to validate the generated YAML.
        """
        self.ai_client = ai_client
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.validate_output = validate_output
        
        # Initialize validator if validation is enabled
        if validate_output:
            self.validator = BDFValidator(use_pydantic=False)
        else:
            self.validator = None
    
    def plan(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Plan a calculation task from user's natural language query.
        
        Args:
            user_query: User's natural language description of the task.
            context: Optional context information.
            **kwargs: Additional parameters to pass to AI client.
        
        Returns:
            Dictionary containing the planned task configuration (YAML structure).
        
        Raises:
            PlanningError: If planning fails.
        """
        if not self.ai_client.is_available():
            raise PlanningError(
                f"AI client is not available. "
                f"Please check your configuration and ensure the AI service is running."
            )
        
        # Build prompts
        system_prompt = build_system_prompt(include_examples=True)
        user_prompt = build_user_prompt(user_query, context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Try planning with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Planning task (attempt {attempt + 1}/{self.max_retries})...")
                
                # Call AI client
                response = self.ai_client.chat(
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    **kwargs
                )
                
                logger.debug(f"AI response received: {response[:200]}...")
                
                # Parse response
                task_config = parse_ai_response(response)
                
                # Validate if enabled
                if self.validate_output and self.validator:
                    try:
                        _, warnings = self.validator.validate(task_config)
                        for warning in warnings:
                            logger.warning(f"Validation warning: {warning}")
                    except ValidationError as e:
                        logger.warning(f"Validation failed: {e}")
                        # Continue anyway - validation is not critical
                
                logger.info("Task planning completed successfully.")
                return task_config
                
            except AIResponseParseError as e:
                last_error = e
                logger.warning(
                    f"Failed to parse AI response (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                
                # If this is not the last attempt, add feedback and retry
                if attempt < self.max_retries - 1:
                    feedback = (
                        "之前的输出格式不正确。请确保输出有效的 YAML 格式，"
                        "并且只包含 YAML 内容，不要添加额外的说明文字。"
                    )
                    messages.append({"role": "assistant", "content": response if 'response' in locals() else ""})
                    messages.append({"role": "user", "content": feedback})
                
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error during planning: {e}")
                if attempt < self.max_retries - 1:
                    continue
                break
        
        # All retries failed
        raise PlanningError(
            f"Failed to plan task after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        ) from last_error
    
    def plan_streaming(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Plan a task with streaming output (returns raw response text).
        
        This is useful for interactive scenarios where you want to show
        the generation progress in real-time.
        
        Args:
            user_query: User's natural language description.
            context: Optional context information.
            **kwargs: Additional parameters.
        
        Yields:
            Text chunks as they are generated.
        """
        if not self.ai_client.is_available():
            raise PlanningError("AI client is not available.")
        
        system_prompt = build_system_prompt(include_examples=True)
        user_prompt = build_user_prompt(user_query, context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        for chunk in self.ai_client.stream_chat(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        ):
            yield chunk
