"""
bdfeasyinput
============

Core library for BDFEasyInput.

This package will gradually implement the full YAML → BDF input translation
pipeline.  At the moment it only contains some low‑level utilities such as
XC functional conversion helpers.
"""

from .xc_functional import (  # noqa: F401
    FunctionalInput,
    FunctionalValidationResult,
    process_functional_input,
    build_dft_functional_lines,
    load_xc_database,
    validate_functional,
)

from .converter import BDFConverter  # noqa: F401
from .validator import BDFValidator, ValidationError  # noqa: F401
from .config import load_config, find_config_file, get_execution_config, get_ai_config, get_analysis_config  # noqa: F401

# Execution module (optional import)
try:
    from .execution import BDFAutotestRunner, BDFDirectRunner, create_runner  # noqa: F401
    __all__ = [
        'BDFConverter',
        'BDFValidator',
        'ValidationError',
        'BDFAutotestRunner',
        'BDFDirectRunner',
        'create_runner',
        'load_config',
        'find_config_file',
        'get_execution_config',
        'get_ai_config',
        'get_analysis_config',
        'FunctionalInput',
        'FunctionalValidationResult',
        'process_functional_input',
        'build_dft_functional_lines',
        'load_xc_database',
        'validate_functional',
    ]
except ImportError:
    __all__ = [
        'BDFConverter',
        'BDFValidator',
        'ValidationError',
        'load_config',
        'find_config_file',
        'get_execution_config',
        'get_ai_config',
        'get_analysis_config',
        'FunctionalInput',
        'FunctionalValidationResult',
        'process_functional_input',
        'build_dft_functional_lines',
        'load_xc_database',
        'validate_functional',
    ]
