"""
BDFEasyInput Converter Module

This module provides functionality to convert YAML input files to BDF input format.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import yaml
import warnings

from .validator import BDFValidator, ValidationError
from .utils import (
    select_scf_method,
    format_coordinates,
    normalize_point_group,
    should_add_saorb
)
from .modules import (
    generate_compass_block,
    generate_xuanyuan_block,
    generate_scf_block,
    generate_tddft_block,
    generate_mp2_block,
    generate_bdfopt_block,
    generate_resp_block
)


class BDFConverter:
    """Converter from YAML configuration to BDF input format."""

    def __init__(self, validate_input: bool = True):
        """
        Initialize the converter.
        
        Args:
            validate_input: Whether to validate input using Pydantic (default: True)
        """
        self.validate_input = validate_input
        self.validator = BDFValidator() if validate_input else None

    def load_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # Utility methods are now imported from utils module
    # Keeping these as wrapper methods for backward compatibility
    def select_scf_method(self, *args, **kwargs):
        """Wrapper for select_scf_method from utils."""
        return select_scf_method(*args, **kwargs)
    
    def format_coordinates(self, *args, **kwargs):
        """Wrapper for format_coordinates from utils."""
        return format_coordinates(*args, **kwargs)
    
    def normalize_point_group(self, group: str) -> Optional[str]:
        """Wrapper for normalize_point_group from utils."""
        return normalize_point_group(group)
    
    def should_add_saorb(self, config: Dict[str, Any]) -> bool:
        """Wrapper for should_add_saorb from utils."""
        return should_add_saorb(config)
    
    # Module generators are now imported from modules package
    # Keeping these as wrapper methods for backward compatibility
    def generate_compass_block(self, config: Dict[str, Any]) -> List[str]:
        """Wrapper for generate_compass_block from modules."""
        return generate_compass_block(config)
    
    def generate_xuanyuan_block(self, config: Dict[str, Any]) -> List[str]:
        """Wrapper for generate_xuanyuan_block from modules."""
        return generate_xuanyuan_block(config)
    
    def generate_scf_block(self, config: Dict[str, Any]) -> List[str]:
        """Wrapper for generate_scf_block from modules."""
        return generate_scf_block(config)
    
    def generate_tddft_block(
        self,
        config: Dict[str, Any],
        tddft_block_settings: Optional[Dict[str, Any]] = None,
        isf: Optional[int] = None,
        istore: Optional[int] = None
    ) -> List[str]:
        """Wrapper for generate_tddft_block from modules."""
        return generate_tddft_block(config, tddft_block_settings, isf, istore)
    
    def generate_bdfopt_block(self, config: Dict[str, Any]) -> List[str]:
        """Wrapper for generate_bdfopt_block from modules."""
        return generate_bdfopt_block(config)
    
    def generate_resp_block(
        self,
        config: Dict[str, Any],
        method: Optional[int] = None,
        norder: Optional[int] = None,
        nfiles: Optional[int] = None,
        iroot: Optional[Union[int, List[int]]] = None
    ) -> List[str]:
        """Wrapper for generate_resp_block from modules."""
        return generate_resp_block(config, method, norder, nfiles, iroot)

    def convert(self, config: Dict[str, Any]) -> str:
        """
        Convert YAML configuration to BDF input format.
        
        Module organization:
        - SCF single point energy: COMPASS → XUANYUAN → SCF
        - TDDFT calculation: COMPASS → XUANYUAN → SCF → TDDFT (one or more blocks)
        - TDDFT-SOC: COMPASS → XUANYUAN → SCF → TDDFT (singlet) → TDDFT (triplet) → TDDFT (SOC)
        - Frequency calculation: COMPASS → BDFOPT (hess only) → XUANYUAN → SCF → RESP (norder 2)
        - Geometry optimization: COMPASS → BDFOPT → XUANYUAN → SCF → RESP
        
        Reference:
        - BDF SCF manual: /Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/SCF.rst
        - BDF TDDFT manual: /Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/TD.rst
        - BDF Optimization manual: /Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Optimization.rst
        
        Args:
            config: YAML configuration dictionary
        
        Returns:
            BDF input file content as string
            
        Raises:
            ValidationError: If input validation fails (when validate_input=True)
        """
        # Validate input if enabled
        if self.validate_input:
            try:
                validated_model, validation_warnings = self.validator.validate(config)
                # Show warnings if any
                for warning in validation_warnings:
                    warnings.warn(warning, UserWarning)
            except ValidationError as e:
                raise ValidationError(f"Input validation failed: {e}") from e
        
        blocks = []
        
        task_type = config.get('task', {}).get('type', 'energy')
        settings = config.get('settings', {})
        tddft_settings = settings.get('tddft', {})
        
        if task_type == 'energy':
            # SCF single point energy calculation module order:
            # 1. COMPASS: Define molecular structure and basis set
            # 2. XUANYUAN: Integral calculation (RS parameter for RS functionals)
            # 3. SCF: SCF calculation settings
            blocks.append(self.generate_compass_block(config))
            blocks.append(self.generate_xuanyuan_block(config))
            blocks.append(self.generate_scf_block(config))
            if settings.get('mp2'):
                blocks.append(generate_mp2_block(config))
        elif task_type == 'tddft':
            # TDDFT calculation module order:
            # 1. COMPASS: Define molecular structure and basis set
            # 2. XUANYUAN: Integral calculation settings
            # 3. SCF: SCF calculation settings
            # 4. TDDFT: One or more TDDFT blocks
            blocks.append(self.generate_compass_block(config))
            blocks.append(self.generate_xuanyuan_block(config))
            blocks.append(self.generate_scf_block(config))
            if settings.get('mp2'):
                blocks.append(generate_mp2_block(config))
            
            # Check for SOC calculation
            soc_settings = tddft_settings.get('soc', {})
            if soc_settings.get('enabled'):
                # TDDFT-SOC requires three TDDFT blocks:
                # 1. Singlet TDDFT (isf=0, istore=1)
                # 2. Triplet TDDFT (isf=1, istore=2)
                # 3. SOC post-processing (isoc=2, nfiles=2)
                singlet_settings = tddft_settings.get('singlet', {})
                triplet_settings = tddft_settings.get('triplet', {})
                
                # First TDDFT: Singlet states
                singlet_config = config.copy()
                if singlet_settings:
                    singlet_config['settings']['tddft'] = {**tddft_settings, **singlet_settings}
                blocks.append(self.generate_tddft_block(singlet_config, tddft_block_settings=singlet_settings, isf=0, istore=1))
                
                # Second TDDFT: Triplet states
                triplet_config = config.copy()
                if triplet_settings:
                    triplet_config['settings']['tddft'] = {**tddft_settings, **triplet_settings}
                blocks.append(self.generate_tddft_block(triplet_config, tddft_block_settings=triplet_settings, isf=1, istore=2))
                
                # Third TDDFT: SOC post-processing
                # TODO: Implement generate_tddft_soc_block method
                # For now, raise NotImplementedError
                raise NotImplementedError("TDDFT-SOC calculation is not yet fully implemented")
            elif tddft_settings.get('singlet') and tddft_settings.get('triplet'):
                # Both singlet and triplet, but no SOC
                singlet_settings = tddft_settings.get('singlet', {})
                triplet_settings = tddft_settings.get('triplet', {})
                
                # First TDDFT: Singlet states
                singlet_config = config.copy()
                singlet_config['settings']['tddft'] = {**tddft_settings, **singlet_settings}
                blocks.append(self.generate_tddft_block(singlet_config, tddft_block_settings=singlet_settings, isf=0))
                
                # Second TDDFT: Triplet states
                triplet_config = config.copy()
                triplet_config['settings']['tddft'] = {**tddft_settings, **triplet_settings}
                blocks.append(self.generate_tddft_block(triplet_config, tddft_block_settings=triplet_settings, isf=1))
            else:
                # Single TDDFT block (default: singlet, isf=0)
                blocks.append(self.generate_tddft_block(config))
        elif task_type == 'optimize':
            # Geometry optimization module order:
            # 1. COMPASS: Define molecular structure and basis set
            # 2. BDFOPT: Structure optimization settings
            # 3. XUANYUAN: Integral calculation settings
            # 4. SCF: SCF calculation settings
            # 5. TDDFT: (optional, for excited state optimization)
            # 6. RESP: Gradient calculation (or Hessian if hess final)
            blocks.append(self.generate_compass_block(config))
            blocks.append(self.generate_bdfopt_block(config))
            blocks.append(self.generate_xuanyuan_block(config))
            blocks.append(self.generate_scf_block(config))
            if settings.get('mp2'):
                blocks.append(generate_mp2_block(config))
            
            # Check for hess final mode (opt+freq)
            opt_settings = settings.get('geometry_optimization', {})
            hess_settings = opt_settings.get('hessian', {})
            hess_mode = hess_settings.get('mode')
            
            # Check for TDDFT excited state optimization
            if settings.get('tddft'):
                blocks.append(self.generate_tddft_block(config, tddft_block_settings=None, istore=1))
                # For TDDFT optimization with hess final, use norder=2
                if hess_mode == 'final':
                    blocks.append(self.generate_resp_block(config, method=2, norder=2, nfiles=1))
                else:
                    blocks.append(self.generate_resp_block(config, method=2, nfiles=1))
            else:
                # Ground state optimization
                # If hess final, calculate Hessian (norder=2) after optimization
                if hess_mode == 'final':
                    blocks.append(self.generate_resp_block(config, method=1, norder=2))
                else:
                    # Regular optimization: only gradient (norder=1)
                    blocks.append(self.generate_resp_block(config, method=1))
        elif task_type == 'frequency':
            # Frequency calculation module order:
            # 1. COMPASS: Define molecular structure and basis set
            # 2. BDFOPT: Hessian calculation settings (hess only)
            # 3. XUANYUAN: Integral calculation settings
            # 4. SCF: SCF calculation settings
            # 5. RESP: Hessian calculation (norder=2)
            blocks.append(self.generate_compass_block(config))
            
            # For frequency calculation, we need to set hess_mode='only' in BDFOPT
            # Create a modified config with hessian settings
            freq_config = config.copy()
            if 'settings' not in freq_config:
                freq_config['settings'] = {}
            if 'geometry_optimization' not in freq_config['settings']:
                freq_config['settings']['geometry_optimization'] = {}
            freq_config['settings']['geometry_optimization']['hessian'] = {'mode': 'only'}
            
            blocks.append(self.generate_bdfopt_block(freq_config))
            blocks.append(self.generate_xuanyuan_block(config))
            blocks.append(self.generate_scf_block(config))
            if settings.get('mp2'):
                blocks.append(generate_mp2_block(config))
            
            # RESP block for Hessian calculation (norder=2)
            # Check if this is TDDFT frequency calculation
            if settings.get('tddft'):
                # TDDFT frequency calculation (excited state frequencies)
                tddft_freq_settings = settings.get('tddft', {})
                nfiles = tddft_freq_settings.get('nfiles', 1)
                iroot = tddft_freq_settings.get('iroot', 1)
                blocks.append(self.generate_tddft_block(config, tddft_block_settings=None, istore=1))
                blocks.append(self.generate_resp_block(config, method=2, norder=2, nfiles=nfiles, iroot=iroot))
            else:
                # Ground state frequency calculation
                blocks.append(self.generate_resp_block(config, method=1, norder=2))
        else:
            raise NotImplementedError(f"Task type '{task_type}' not yet implemented")
        
        # Join all blocks with blank lines
        result_lines = []
        for block in blocks:
            result_lines.extend(block)
            result_lines.append("")  # Blank line between blocks
        
        return '\n'.join(result_lines)

    def convert_file(self, yaml_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert YAML file to BDF input file.
        
        Args:
            yaml_path: Path to input YAML file
            output_path: Path to output BDF file (optional, defaults to .inp extension)
        
        Returns:
            Path to generated BDF file
        """
        config = self.load_yaml(yaml_path)
        bdf_content = self.convert(config)
        
        if output_path is None:
            yaml_file = Path(yaml_path)
            output_path = str(yaml_file.with_suffix('.inp'))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bdf_content)
        
        return output_path

