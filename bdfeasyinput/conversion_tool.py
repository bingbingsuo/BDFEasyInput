"""
Conversion Tool Module

This module provides enhanced utilities for converting YAML files to BDF input format,
including batch conversion, validation, and preview functionality.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import yaml
import logging

from .converter import BDFConverter
from .validator import BDFValidator, ValidationError
from .yaml_generator import YAMLGenerator

logger = logging.getLogger(__name__)


class ConversionTool:
    """Enhanced tool for YAML to BDF conversion."""
    
    def __init__(
        self,
        validate_input: bool = True,
        validate_output: bool = False
    ):
        """
        Initialize the conversion tool.
        
        Args:
            validate_input: Whether to validate input YAML (default: True)
            validate_output: Whether to validate output BDF (default: False)
        """
        self.converter = BDFConverter(validate_input=validate_input)
        self.validator = BDFValidator() if validate_input else None
        self.validate_output = validate_output
        self.yaml_generator = YAMLGenerator(validate_output=validate_input)
    
    def convert_file(
        self,
        yaml_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        overwrite: bool = False
    ) -> Path:
        """
        Convert YAML file to BDF input file.
        
        Args:
            yaml_path: Path to input YAML file
            output_path: Path to output BDF file (if None, uses .inp extension)
            overwrite: Whether to overwrite existing output file
        
        Returns:
            Path to generated BDF file
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValidationError: If input validation fails
            FileExistsError: If output file exists and overwrite=False
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        # Determine output path
        if output_path is None:
            output_path = yaml_path.with_suffix('.inp')
        else:
            output_path = Path(output_path)
        
        # Check if output exists
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path}. "
                f"Use overwrite=True to overwrite."
            )
        
        # Load and convert
        config = self.yaml_generator.load_yaml(yaml_path)
        bdf_content = self.converter.convert(config)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bdf_content)
        
        logger.info(f"Converted {yaml_path} -> {output_path}")
        return output_path
    
    def convert_dict(
        self,
        config: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        overwrite: bool = False
    ) -> Union[str, Path]:
        """
        Convert YAML configuration dictionary to BDF input.
        
        Args:
            config: YAML configuration dictionary
            output_path: Optional path to save BDF file
            overwrite: Whether to overwrite existing file
        
        Returns:
            BDF content string if output_path is None, else Path to file
        """
        bdf_content = self.converter.convert(config)
        
        if output_path is None:
            return bdf_content
        
        output_path = Path(output_path)
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path}. "
                f"Use overwrite=True to overwrite."
            )
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bdf_content)
        
        logger.info(f"Saved BDF input to {output_path}")
        return output_path
    
    def batch_convert(
        self,
        yaml_files: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        overwrite: bool = False,
        continue_on_error: bool = True
    ) -> Dict[str, Union[Path, Exception]]:
        """
        Convert multiple YAML files to BDF input files.
        
        Args:
            yaml_files: List of YAML file paths
            output_dir: Optional output directory (if None, uses same directory as input)
            overwrite: Whether to overwrite existing files
            continue_on_error: Whether to continue on errors
        
        Returns:
            Dictionary mapping input paths to output paths or exceptions
        """
        results = {}
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        for yaml_file in yaml_files:
            yaml_path = Path(yaml_file)
            
            try:
                # Determine output path
                if output_dir:
                    output_path = output_dir / yaml_path.with_suffix('.inp').name
                else:
                    output_path = yaml_path.with_suffix('.inp')
                
                result_path = self.convert_file(
                    yaml_path,
                    output_path=output_path,
                    overwrite=overwrite
                )
                results[str(yaml_path)] = result_path
                
            except Exception as e:
                logger.error(f"Failed to convert {yaml_path}: {e}")
                results[str(yaml_path)] = e
                
                if not continue_on_error:
                    raise
        
        return results
    
    def preview(
        self,
        yaml_path: Union[str, Path],
        max_lines: Optional[int] = 50
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Preview BDF input without saving to file.
        
        Args:
            yaml_path: Path to YAML file
            max_lines: Maximum number of lines to return (None for all)
        
        Returns:
            Tuple of (BDF content preview, full config dictionary)
        """
        config = self.yaml_generator.load_yaml(yaml_path)
        bdf_content = self.converter.convert(config)
        
        lines = bdf_content.split('\n')
        if max_lines and len(lines) > max_lines:
            preview_lines = lines[:max_lines]
            preview = '\n'.join(preview_lines) + f"\n... ({len(lines) - max_lines} more lines)"
        else:
            preview = bdf_content
        
        return preview, config
    
    def validate_yaml(
        self,
        yaml_path: Union[str, Path]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate YAML file without converting.
        
        Args:
            yaml_path: Path to YAML file
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        if not self.validator:
            raise RuntimeError("Validator not initialized")
        
        config = self.yaml_generator.load_yaml(yaml_path)
        
        try:
            validated_model, warnings = self.validator.validate(config)
            return True, [], warnings
        except ValidationError as e:
            return False, [str(e)], []
    
    def convert_from_xyz(
        self,
        xyz_path: Union[str, Path],
        task_type: str = 'energy',
        charge: int = 0,
        multiplicity: int = 1,
        method: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        overwrite: bool = False
    ) -> Path:
        """
        Convert XYZ file directly to BDF input file.
        
        Args:
            xyz_path: Path to XYZ file
            task_type: Type of calculation
            charge: Molecular charge
            multiplicity: Spin multiplicity
            method: Method configuration
            settings: Optional settings
            output_path: Optional output BDF file path
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to generated BDF file
        """
        # Generate YAML from XYZ
        config = self.yaml_generator.generate_from_xyz(
            xyz_path=xyz_path,
            task_type=task_type,
            charge=charge,
            multiplicity=multiplicity,
            method=method,
            settings=settings
        )
        
        # Determine output path
        if output_path is None:
            output_path = Path(xyz_path).with_suffix('.inp')
        else:
            output_path = Path(output_path)
        
        # Check if output exists
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path}. "
                f"Use overwrite=True to overwrite."
            )
        
        # Convert to BDF
        bdf_content = self.converter.convert(config)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bdf_content)
        
        logger.info(f"Converted XYZ {xyz_path} -> BDF {output_path}")
        return output_path


def convert_yaml_to_bdf(
    yaml_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    validate: bool = True,
    overwrite: bool = False
) -> Path:
    """
    Convenience function to convert YAML to BDF.
    
    Args:
        yaml_path: Path to input YAML file
        output_path: Optional output BDF file path
        validate: Whether to validate input
        overwrite: Whether to overwrite existing file
    
    Returns:
        Path to generated BDF file
    """
    tool = ConversionTool(validate_input=validate)
    return tool.convert_file(yaml_path, output_path, overwrite=overwrite)


def batch_convert_yaml(
    yaml_files: List[Union[str, Path]],
    output_dir: Optional[Union[str, Path]] = None,
    validate: bool = True,
    overwrite: bool = False
) -> Dict[str, Union[Path, Exception]]:
    """
    Convenience function for batch conversion.
    
    Args:
        yaml_files: List of YAML file paths
        output_dir: Optional output directory
        validate: Whether to validate inputs
        overwrite: Whether to overwrite existing files
    
    Returns:
        Dictionary mapping input paths to output paths or exceptions
    """
    tool = ConversionTool(validate_input=validate)
    return tool.batch_convert(yaml_files, output_dir, overwrite)
