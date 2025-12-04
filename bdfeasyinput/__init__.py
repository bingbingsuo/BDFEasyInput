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


