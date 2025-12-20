"""
YAML Generator Module

This module provides utilities for generating BDF calculation task YAML files
from various input formats and templates.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import yaml
import re

from .validator import BDFValidator, ValidationError


class YAMLGenerator:
    """Generator for BDF calculation task YAML files."""
    
    def __init__(self, validate_output: bool = True):
        """
        Initialize the YAML generator.
        
        Args:
            validate_output: Whether to validate generated YAML (default: True)
        """
        self.validate_output = validate_output
        self.validator = BDFValidator() if validate_output else None
    
    def generate_from_template(
        self,
        task_type: str,
        molecule: Dict[str, Any],
        method: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate YAML configuration from template parameters.
        
        Args:
            task_type: Type of calculation (energy, optimize, frequency, tddft)
            molecule: Molecule configuration (charge, multiplicity, coordinates, etc.)
            method: Method configuration (type, functional, basis, etc.)
            settings: Optional settings dictionary
            description: Optional task description
        
        Returns:
            YAML configuration dictionary
        
        Raises:
            ValidationError: If validation fails and validate_output=True
        """
        config = {
            'task': {
                'type': task_type
            },
            'molecule': molecule,
            'method': method
        }
        
        if description:
            config['task']['description'] = description
        
        if settings:
            config['settings'] = settings
        
        # Validate if enabled
        if self.validate_output and self.validator:
            try:
                validated_model, warnings = self.validator.validate(config)
                for warning in warnings:
                    import warnings as py_warnings
                    py_warnings.warn(warning, UserWarning)
            except ValidationError as e:
                raise ValidationError(f"Generated YAML validation failed: {e}") from e
        
        return config
    
    def generate_from_xyz(
        self,
        xyz_path: Union[str, Path],
        task_type: str = 'energy',
        charge: int = 0,
        multiplicity: int = 1,
        method: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate YAML configuration from XYZ file.
        
        Args:
            xyz_path: Path to XYZ file
            task_type: Type of calculation (default: 'energy')
            charge: Molecular charge (default: 0)
            multiplicity: Spin multiplicity (default: 1)
            method: Method configuration (if None, uses default)
            settings: Optional settings dictionary
            name: Optional molecule name (if None, uses filename)
        
        Returns:
            YAML configuration dictionary
        """
        xyz_path = Path(xyz_path)
        if not xyz_path.exists():
            raise FileNotFoundError(f"XYZ file not found: {xyz_path}")
        
        # Read XYZ file
        with open(xyz_path, 'r') as f:
            lines = f.readlines()
        
        # Parse XYZ format
        # First line: number of atoms (optional)
        # Second line: comment/name (optional)
        # Remaining lines: atom_symbol x y z
        
        coordinates = []
        start_idx = 0
        
        # Skip first line if it's a number
        if len(lines) > 0 and lines[0].strip().isdigit():
            start_idx = 2  # Skip number and comment line
        elif len(lines) > 0:
            start_idx = 1  # Skip comment line
        
        # Parse coordinates
        for line in lines[start_idx:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 4:
                atom_symbol = parts[0]
                x, y, z = map(float, parts[1:4])
                coordinates.append(f"{atom_symbol} {x:.10f} {y:.10f} {z:.10f}")
        
        # Determine molecule name
        if name is None:
            name = xyz_path.stem
        
        # Default method if not provided
        if method is None:
            method = {
                'type': 'dft',
                'functional': 'pbe0',
                'basis': 'cc-pvdz'
            }
        
        # Build molecule configuration
        molecule = {
            'name': name,
            'charge': charge,
            'multiplicity': multiplicity,
            'coordinates': coordinates,
            'units': 'angstrom'
        }
        
        return self.generate_from_template(
            task_type=task_type,
            molecule=molecule,
            method=method,
            settings=settings,
            description=f"{name} {task_type} calculation"
        )
    
    def generate_template(
        self,
        task_type: str,
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a template YAML configuration for a given task type.
        
        Args:
            task_type: Type of calculation (energy, optimize, frequency, tddft)
            include_comments: Whether to include comment fields in the template
        
        Returns:
            Template YAML configuration dictionary
        """
        templates = {
            'energy': {
                'task': {
                    'type': 'energy',
                    'description': 'Single point energy calculation'
                },
                'molecule': {
                    'name': 'Molecule',
                    'charge': 0,
                    'multiplicity': 1,
                    'coordinates': [
                        '# Format: ATOM X Y Z (units: angstrom)',
                        '# Example:',
                        '# - O  0.0000 0.0000 0.1173',
                        '# - H  0.0000 0.7572 -0.4692',
                        '# - H  0.0000 -0.7572 -0.4692'
                    ],
                    'units': 'angstrom'
                },
                'method': {
                    'type': 'dft',
                    'functional': 'pbe0',
                    'basis': 'cc-pvdz'
                },
                'settings': {
                    'scf': {
                        'convergence': 1e-6,
                        'max_iterations': 100
                    }
                }
            },
            'optimize': {
                'task': {
                    'type': 'optimize',
                    'description': 'Geometry optimization'
                },
                'molecule': {
                    'name': 'Molecule',
                    'charge': 0,
                    'multiplicity': 1,
                    'coordinates': [
                        '# Format: ATOM X Y Z (units: angstrom)'
                    ],
                    'units': 'angstrom'
                },
                'method': {
                    'type': 'dft',
                    'functional': 'pbe0',
                    'basis': 'cc-pvdz'
                },
                'settings': {
                    'scf': {
                        'convergence': 1e-6,
                        'max_iterations': 100
                    },
                    'geometry_optimization': {
                        'max_iterations': 50,
                        'convergence': {
                            'energy': 1e-6,
                            'gradient': 1e-4,
                            'displacement': 1e-4
                        }
                    }
                }
            },
            'frequency': {
                'task': {
                    'type': 'frequency',
                    'description': 'Frequency calculation'
                },
                'molecule': {
                    'name': 'Molecule',
                    'charge': 0,
                    'multiplicity': 1,
                    'coordinates': [
                        '# Format: ATOM X Y Z (units: angstrom)'
                    ],
                    'units': 'angstrom'
                },
                'method': {
                    'type': 'dft',
                    'functional': 'pbe0',
                    'basis': 'cc-pvdz'
                },
                'settings': {
                    'scf': {
                        'convergence': 1e-6,
                        'max_iterations': 100
                    }
                }
            },
            'tddft': {
                'task': {
                    'type': 'tddft',
                    'description': 'TDDFT excited state calculation'
                },
                'molecule': {
                    'name': 'Molecule',
                    'charge': 0,
                    'multiplicity': 1,
                    'coordinates': [
                        '# Format: ATOM X Y Z (units: angstrom)'
                    ],
                    'units': 'angstrom'
                },
                'method': {
                    'type': 'dft',
                    'functional': 'pbe0',
                    'basis': 'cc-pvdz'
                },
                'settings': {
                    'scf': {
                        'convergence': 1e-6,
                        'max_iterations': 100
                    },
                    'tddft': {
                        'nstates': 10,
                        'singlet': True,
                        'triplet': False
                    }
                }
            }
        }
        
        if task_type not in templates:
            raise ValueError(
                f"Unknown task type: {task_type}. "
                f"Supported types: {list(templates.keys())}"
            )
        
        template = templates[task_type].copy()
        
        # Remove comments if not requested
        if not include_comments:
            if 'coordinates' in template['molecule']:
                template['molecule']['coordinates'] = [
                    line for line in template['molecule']['coordinates']
                    if not line.strip().startswith('#')
                ]
        
        return template
    
    def save_yaml(
        self,
        config: Dict[str, Any],
        output_path: Union[str, Path],
        **kwargs
    ) -> Path:
        """
        Save YAML configuration to file.
        
        Args:
            config: YAML configuration dictionary
            output_path: Path to output file
            **kwargs: Additional arguments to yaml.dump
        
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_kwargs = {
            'default_flow_style': False,
            'allow_unicode': True,
            'sort_keys': False
        }
        default_kwargs.update(kwargs)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, **default_kwargs)
        
        return output_path
    
    def load_yaml(self, yaml_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load YAML configuration from file.
        
        Args:
            yaml_path: Path to YAML file
        
        Returns:
            YAML configuration dictionary
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def update_config(
        self,
        config: Dict[str, Any],
        updates: Dict[str, Any],
        merge: bool = True
    ) -> Dict[str, Any]:
        """
        Update YAML configuration with new values.
        
        Args:
            config: Original configuration dictionary
            updates: Dictionary of updates to apply
            merge: If True, merge nested dictionaries; if False, replace
        
        Returns:
            Updated configuration dictionary
        """
        if not merge:
            config = config.copy()
            config.update(updates)
            return config
        
        # Deep merge
        result = config.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.update_config(result[key], value, merge=True)
            else:
                result[key] = value
        
        return result


def generate_yaml_from_xyz(
    xyz_path: Union[str, Path],
    task_type: str = 'energy',
    charge: int = 0,
    multiplicity: int = 1,
    method: Optional[Dict[str, Any]] = None,
    settings: Optional[Dict[str, Any]] = None,
    output_path: Optional[Union[str, Path]] = None,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to generate YAML from XYZ file.
    
    Args:
        xyz_path: Path to XYZ file
        task_type: Type of calculation
        charge: Molecular charge
        multiplicity: Spin multiplicity
        method: Method configuration
        settings: Optional settings
        output_path: Optional path to save YAML file
        validate: Whether to validate output
    
    Returns:
        YAML configuration dictionary
    """
    generator = YAMLGenerator(validate_output=validate)
    config = generator.generate_from_xyz(
        xyz_path=xyz_path,
        task_type=task_type,
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        settings=settings
    )
    
    if output_path:
        generator.save_yaml(config, output_path)
    
    return config


def generate_yaml_template(
    task_type: str,
    output_path: Optional[Union[str, Path]] = None,
    include_comments: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to generate YAML template.
    
    Args:
        task_type: Type of calculation
        output_path: Optional path to save template file
        include_comments: Whether to include comments
    
    Returns:
        Template YAML configuration dictionary
    """
    generator = YAMLGenerator(validate_output=False)
    template = generator.generate_template(task_type, include_comments=include_comments)
    
    if output_path:
        generator.save_yaml(template, output_path)
    
    return template
