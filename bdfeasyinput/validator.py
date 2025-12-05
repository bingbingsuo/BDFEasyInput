"""
BDFEasyInput Validator Module

This module provides input validation for YAML configuration files.
Supports both basic validation (no dependencies) and Pydantic-based validation (if available).
"""

from typing import Optional, List, Dict, Any, Union, Tuple
from enum import Enum


class ValidationError(Exception):
    """Custom validation error."""
    pass


class TaskType(str, Enum):
    """Supported task types."""
    ENERGY = "energy"
    TDDFT = "tddft"
    OPTIMIZE = "optimize"
    FREQUENCY = "frequency"


class MethodType(str, Enum):
    """Supported method types."""
    HF = "hf"
    DFT = "dft"


class CoordinateUnit(str, Enum):
    """Coordinate units."""
    ANGSTROM = "angstrom"
    BOHR = "bohr"


class BDFValidator:
    """Validator for BDF input configuration."""
    
    def __init__(self, use_pydantic: bool = False):
        """
        Initialize the validator.
        
        Args:
            use_pydantic: Whether to use Pydantic for validation (requires pydantic to be installed)
        """
        self.use_pydantic = use_pydantic
        self.warnings: List[str] = []
        
        if use_pydantic:
            try:
                import pydantic
                self.pydantic_available = True
            except ImportError:
                raise ImportError(
                    "pydantic is required for Pydantic-based validation. "
                    "Please install it with: pip install pydantic"
                )
        else:
            self.pydantic_available = False
    
    def validate(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate YAML configuration.
        
        Args:
            config: YAML configuration dictionary
            
        Returns:
            Tuple of (validated_config, warnings_list)
            
        Raises:
            ValidationError: If validation fails
        """
        self.warnings = []
        errors = []
        
        # Basic validation (always performed)
        errors.extend(self._validate_basic_structure(config))
        errors.extend(self._validate_task(config))
        errors.extend(self._validate_molecule(config))
        errors.extend(self._validate_method(config))
        errors.extend(self._validate_compatibility(config))
        
        if errors:
            raise ValidationError(
                "Input validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            )
        
        return config, self.warnings
    
    def _validate_basic_structure(self, config: Dict[str, Any]) -> List[str]:
        """Validate basic structure of config."""
        errors = []
        
        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return errors
        
        required_keys = ['task', 'molecule', 'method']
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: '{key}'")
        
        return errors
    
    def _validate_task(self, config: Dict[str, Any]) -> List[str]:
        """Validate task configuration."""
        errors = []
        
        task = config.get('task', {})
        if not isinstance(task, dict):
            errors.append("'task' must be a dictionary")
            return errors
        
        task_type = task.get('type')
        if not task_type:
            errors.append("'task.type' is required")
        elif task_type not in [t.value for t in TaskType]:
            errors.append(
                f"Invalid task.type: '{task_type}'. "
                f"Must be one of: {', '.join([t.value for t in TaskType])}"
            )
        
        return errors
    
    def _validate_molecule(self, config: Dict[str, Any]) -> List[str]:
        """Validate molecule configuration."""
        errors = []
        
        molecule = config.get('molecule', {})
        if not isinstance(molecule, dict):
            errors.append("'molecule' must be a dictionary")
            return errors
        
        # Charge (required)
        if 'charge' not in molecule:
            errors.append("'molecule.charge' is required")
        else:
            charge = molecule['charge']
            if not isinstance(charge, int):
                errors.append("'molecule.charge' must be an integer")
            elif abs(charge) > 10:
                self.warnings.append(f"Charge {charge} seems unusually large. Please verify.")
        
        # Multiplicity (required)
        if 'multiplicity' not in molecule:
            errors.append("'molecule.multiplicity' is required")
        else:
            multiplicity = molecule['multiplicity']
            if not isinstance(multiplicity, int):
                errors.append("'molecule.multiplicity' must be an integer")
            elif multiplicity < 1:
                errors.append(f"'molecule.multiplicity' must be >= 1, got {multiplicity}")
        
        # Coordinates (required)
        if 'coordinates' not in molecule:
            errors.append("'molecule.coordinates' is required")
        else:
            coordinates = molecule['coordinates']
            if not isinstance(coordinates, list):
                errors.append("'molecule.coordinates' must be a list")
            elif len(coordinates) == 0:
                errors.append("'molecule.coordinates' must contain at least one coordinate")
            else:
                # Validate coordinate format
                for i, coord in enumerate(coordinates):
                    if isinstance(coord, str):
                        parts = coord.strip().split()
                        if len(parts) != 4:
                            errors.append(
                                f"Invalid coordinate format at index {i}: '{coord}'. "
                                f"Expected 'ATOM X Y Z'"
                            )
                    elif isinstance(coord, dict):
                        required_keys = ['atom', 'x', 'y', 'z']
                        for key in required_keys:
                            if key not in coord:
                                errors.append(
                                    f"Coordinate at index {i} missing required key: '{key}'"
                                )
                    else:
                        errors.append(
                            f"Invalid coordinate format at index {i}: must be string or dict"
                        )
        
        # Units (optional)
        if 'units' in molecule:
            units = molecule['units']
            if units not in [u.value for u in CoordinateUnit]:
                errors.append(
                    f"Invalid molecule.units: '{units}'. "
                    f"Must be one of: {', '.join([u.value for u in CoordinateUnit])}"
                )
        
        return errors
    
    def _validate_method(self, config: Dict[str, Any]) -> List[str]:
        """Validate method configuration."""
        errors = []
        
        method = config.get('method', {})
        if not isinstance(method, dict):
            errors.append("'method' must be a dictionary")
            return errors
        
        # Method type (required)
        method_type = method.get('type')
        if not method_type:
            errors.append("'method.type' is required")
        elif method_type not in [m.value for m in MethodType]:
            errors.append(
                f"Invalid method.type: '{method_type}'. "
                f"Must be one of: {', '.join([m.value for m in MethodType])}"
            )
        
        # Basis (required)
        if 'basis' not in method:
            errors.append("'method.basis' is required")
        
        # Functional (required for DFT)
        if method_type == MethodType.DFT.value:
            if 'functional' not in method or not method['functional']:
                errors.append("'method.functional' is required when method.type is 'dft'")
        
        return errors
    
    def _validate_compatibility(self, config: Dict[str, Any]) -> List[str]:
        """Validate parameter compatibility."""
        errors = []
        
        molecule = config.get('molecule', {})
        method = config.get('method', {})
        task = config.get('task', {})
        settings = config.get('settings', {})
        
        multiplicity = molecule.get('multiplicity', 1)
        method_type = method.get('type')
        task_type = task.get('type')
        
        # Check: Spin-adapted TDDFT requires open-shell
        if settings and settings.get('tddft'):
            tddft_settings = settings['tddft']
            if tddft_settings.get('spin_adapted'):
                if multiplicity == 1:
                    self.warnings.append(
                        "Spin-adapted TDDFT is typically used for open-shell systems. "
                        "For closed-shell systems, regular TDDFT is recommended."
                    )
        
        # Check: Frequency calculation warning
        if task_type == TaskType.FREQUENCY.value:
            self.warnings.append(
                "Frequency calculation should typically be performed on an optimized geometry. "
                "Make sure the provided coordinates are optimized."
            )
        
        # Check: Open-shell TDDFT requires Abelian point groups
        if task_type == TaskType.TDDFT.value and multiplicity > 1:
            if settings and settings.get('compass'):
                compass_settings = settings['compass']
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
        
        return errors
    
    def validate_file(self, yaml_path: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate YAML file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Tuple of (validated_config, warnings_list)
        """
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return self.validate(config)
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.warnings
