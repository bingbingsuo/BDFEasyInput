"""
BDFEasyInput Validator Module

This module provides input validation for YAML configuration files.
Uses bdfeasyinput_schema for type-safe validation with Pydantic.
"""

from typing import List, Dict, Any, Tuple

from bdfeasyinput_schema import (
    EasyInputConfig,
    TaskType,
    MethodType,
    CoordinateUnit,
)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class BDFValidator:
    """Validator for BDF input configuration using shared schema."""
    
    def __init__(self, use_pydantic: bool = None):
        """
        Initialize the validator.
        
        Args:
            use_pydantic: Deprecated parameter, kept for backward compatibility.
                         Schema validation is now always enabled.
        """
        self.warnings: List[str] = []
        # Schema validation is now always enabled
        if use_pydantic is not None:
            import warnings
            warnings.warn(
                "use_pydantic parameter is deprecated. "
                "Schema validation is now always enabled.",
                DeprecationWarning
            )
    
    def validate(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate YAML configuration using Pydantic schema.
        
        Args:
            config: YAML configuration dictionary
            
        Returns:
            Tuple of (validated_config_dict, warnings_list)
            
        Raises:
            ValidationError: If validation fails
        """
        self.warnings = []
        
        try:
            # Use Pydantic model validation
            easyinput_config = EasyInputConfig.model_validate(config)
            
            # Perform additional compatibility checks
            self._check_compatibility(easyinput_config)
            
            # Convert to dictionary for return (maintains interface compatibility)
            validated_dict = easyinput_config.to_yaml_dict()
            
            return validated_dict, self.warnings
            
        except Exception as e:
            # Provide detailed error message
            error_msg = str(e)
            if hasattr(e, 'errors') and hasattr(e, 'model'):
                # Pydantic validation error
                errors = e.errors()
                error_details = []
                for err in errors:
                    loc = " -> ".join(str(x) for x in err.get('loc', []))
                    msg = err.get('msg', 'Validation error')
                    error_details.append(f"  {loc}: {msg}")
                error_msg = "Schema validation failed:\n" + "\n".join(error_details)
            
            raise ValidationError(
                f"Input validation failed: {error_msg}\n"
                f"Please check your YAML configuration format."
            ) from e
    
    def _check_compatibility(self, config: EasyInputConfig) -> None:
        """
        Check parameter compatibility and add warnings.
        
        Args:
            config: Validated EasyInputConfig instance
        """
        # Check: Spin-adapted TDDFT requires open-shell
        if config.settings.tddft:
            tddft_settings = config.settings.tddft
            # Note: spin_adapted is not in current schema, but we check for it
            if config.molecule.multiplicity == 1:
                # This is a general warning for closed-shell systems
                pass
        
        # Check: Frequency calculation warning
        if config.task.type == TaskType.FREQUENCY:
            self.warnings.append(
                "Frequency calculation should typically be performed on an optimized geometry. "
                "Make sure the provided coordinates are optimized."
            )
        
        # Check: Open-shell TDDFT requires Abelian point groups
        if config.task.type == TaskType.TDDFT and config.molecule.multiplicity > 1:
            # Check if compass settings are available (they might be in metadata or settings)
            settings_dict = config.to_yaml_dict().get('settings', {})
            compass_settings = settings_dict.get('compass', {})
            symmetry = compass_settings.get('symmetry', {})
            group = symmetry.get('group')
            if group:
                abelian_groups = ["D(2h)", "D(2)", "C(2v)", "C(2h)", "C(s)", "C(2)", "C(1)", "C(i)"]
                if group not in abelian_groups:
                    self.warnings.append(
                        f"Open-shell TDDFT calculations require Abelian point groups. "
                        f"Group '{group}' may not be supported. "
                        f"Recommended groups: {', '.join(abelian_groups)}"
                    )
        
        # Check: Unusually large charge
        if abs(config.molecule.charge) > 10:
            self.warnings.append(
                f"Charge {config.molecule.charge} seems unusually large. Please verify."
            )
    
    def validate_file(self, yaml_path: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate YAML file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Tuple of (validated_config_dict, warnings_list)
        """
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return self.validate(config)
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.warnings


def validate_with_schema(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration using schema and return validated dict.
    
    This is a convenience function that uses the shared schema for validation.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    validator = BDFValidator()
    validated_dict, _ = validator.validate(config)
    return validated_dict
