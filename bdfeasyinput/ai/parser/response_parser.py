"""
AI Response Parser

This module provides functionality to parse AI responses and extract YAML content.
"""

import re
import yaml
from typing import Dict, Any, Optional


class AIResponseParseError(Exception):
    """Error raised when parsing AI response fails."""
    pass


def extract_yaml_from_response(response: str) -> str:
    """
    Extract YAML content from AI response.
    
    AI responses may contain:
    - Plain YAML text
    - YAML wrapped in code blocks (```yaml ... ```)
    - YAML wrapped in code blocks (``` ... ```)
    - Explanatory text before/after YAML
    
    Args:
        response: Raw AI response text.
    
    Returns:
        Extracted YAML content as a string.
    
    Raises:
        AIResponseParseError: If no valid YAML can be extracted.
    """
    # Try to find YAML in code blocks first
    # Pattern: ```yaml ... ``` or ``` ... ```
    yaml_block_pattern = r'```(?:yaml)?\s*\n(.*?)\n```'
    matches = re.findall(yaml_block_pattern, response, re.DOTALL)
    
    if matches:
        # Use the first (and usually only) YAML block
        yaml_content = matches[0].strip()
        return yaml_content
    
    # Try to find YAML without code blocks
    # Look for lines that start with a key (like "task:", "molecule:", etc.)
    lines = response.split('\n')
    yaml_start = None
    yaml_end = None
    
    # Common YAML root keys in our format
    root_keys = ['task:', 'molecule:', 'method:', 'settings:']
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check if line starts with a root key
        if any(stripped.startswith(key) for key in root_keys):
            yaml_start = i
            break
    
    if yaml_start is not None:
        # Find where YAML ends (first non-indented line after YAML starts)
        # or end of text
        yaml_end = len(lines)
        for i in range(yaml_start + 1, len(lines)):
            line = lines[i]
            # Stop if we hit a line that's not empty and not indented
            # and doesn't look like YAML
            if line.strip() and not line.startswith((' ', '\t', '-', '#')):
                # But allow if it looks like a YAML key
                if not any(line.strip().endswith(':') for _ in [1]):
                    yaml_end = i
                    break
        
        yaml_content = '\n'.join(lines[yaml_start:yaml_end]).strip()
        return yaml_content
    
    # If we can't find structured YAML, try parsing the whole response
    # This might work if the response is pure YAML
    try:
        # Try to parse as YAML to see if it's valid
        yaml.safe_load(response)
        return response.strip()
    except yaml.YAMLError:
        pass
    
    # Last resort: try to extract anything that looks like YAML
    # Look for lines with colons (key-value pairs)
    yaml_lines = []
    for line in lines:
        if ':' in line or line.strip().startswith('-'):
            yaml_lines.append(line)
    
    if yaml_lines:
        yaml_content = '\n'.join(yaml_lines)
        return yaml_content
    
    raise AIResponseParseError(
        "Could not extract YAML from AI response. "
        "Response should contain YAML format content."
    )


def validate_yaml_content(yaml_content: str) -> bool:
    """
    Validate that the extracted YAML content is well-formed.
    
    Args:
        yaml_content: YAML content string.
    
    Returns:
        True if YAML is valid, False otherwise.
    """
    try:
        yaml.safe_load(yaml_content)
        return True
    except yaml.YAMLError:
        return False


def parse_ai_response(response: str) -> Dict[str, Any]:
    """
    Parse AI response and extract structured YAML data.
    
    This is the main entry point for parsing AI responses.
    
    Args:
        response: Raw AI response text.
    
    Returns:
        Parsed YAML as a dictionary.
    
    Raises:
        AIResponseParseError: If parsing fails.
    """
    # Extract YAML content
    yaml_content = extract_yaml_from_response(response)
    
    # Validate YAML
    if not validate_yaml_content(yaml_content):
        raise AIResponseParseError(
            f"Extracted YAML is not valid. Content:\n{yaml_content}"
        )
    
    # Parse YAML
    try:
        parsed_data = yaml.safe_load(yaml_content)
        
        if parsed_data is None:
            raise AIResponseParseError("Parsed YAML is empty.")
        
        if not isinstance(parsed_data, dict):
            raise AIResponseParseError(
                f"Parsed YAML must be a dictionary, got {type(parsed_data)}"
            )
        
        return parsed_data
    except yaml.YAMLError as e:
        raise AIResponseParseError(f"Failed to parse YAML: {e}") from e

