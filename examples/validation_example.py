#!/usr/bin/env python3
"""
Validation Example

This script demonstrates the input validation functionality.
"""

from bdfeasyinput import BDFValidator, BDFConverter, ValidationError
import yaml
import warnings


def test_validation():
    """Test input validation."""
    
    print("=" * 70)
    print("BDFEasyInput Input Validation Example")
    print("=" * 70)
    print()
    
    validator = BDFValidator()
    
    # Example 1: Valid input
    print("Example 1: Valid input")
    print("-" * 70)
    with open('h2o_rhf.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        validated_config, warnings_list = validator.validate(config)
        print("✓ Validation passed")
        if warnings_list:
            print(f"  Warnings ({len(warnings_list)}):")
            for w in warnings_list:
                print(f"    - {w}")
        else:
            print("  No warnings")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
    print()
    
    # Example 2: Missing required field
    print("Example 2: Missing required field (charge)")
    print("-" * 70)
    invalid_config = {
        'task': {'type': 'energy'},
        'molecule': {
            'multiplicity': 1,
            'coordinates': ['O 0 0 0', 'H 0 0 1']
        },
        'method': {'type': 'hf', 'basis': 'cc-pvdz'}
    }
    
    try:
        validated_config, warnings_list = validator.validate(invalid_config)
        print("✗ Should have failed")
    except ValidationError as e:
        print("✓ Validation correctly caught error")
        print(f"  Error message:")
        for line in str(e).split('\n'):
            print(f"    {line}")
    print()
    
    # Example 3: Invalid parameter value
    print("Example 3: Invalid parameter value (multiplicity < 1)")
    print("-" * 70)
    invalid_config2 = {
        'task': {'type': 'energy'},
        'molecule': {
            'charge': 0,
            'multiplicity': 0,  # Invalid
            'coordinates': ['O 0 0 0', 'H 0 0 1']
        },
        'method': {'type': 'hf', 'basis': 'cc-pvdz'}
    }
    
    try:
        validated_config, warnings_list = validator.validate(invalid_config2)
        print("✗ Should have failed")
    except ValidationError as e:
        print("✓ Validation correctly caught error")
        print(f"  Error message:")
        for line in str(e).split('\n'):
            print(f"    {line}")
    print()
    
    # Example 4: DFT without functional
    print("Example 4: DFT method without functional")
    print("-" * 70)
    invalid_config3 = {
        'task': {'type': 'energy'},
        'molecule': {
            'charge': 0,
            'multiplicity': 1,
            'coordinates': ['O 0 0 0', 'H 0 0 1']
        },
        'method': {'type': 'dft', 'basis': 'cc-pvdz'}  # Missing functional
    }
    
    try:
        validated_config, warnings_list = validator.validate(invalid_config3)
        print("✗ Should have failed")
    except ValidationError as e:
        print("✓ Validation correctly caught error")
        print(f"  Error message:")
        for line in str(e).split('\n'):
            print(f"    {line}")
    print()
    
    # Example 5: Converter with validation
    print("Example 5: Converter with automatic validation")
    print("-" * 70)
    converter = BDFConverter(validate_input=True)
    
    with open('h2o_rhf.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            bdf_output = converter.convert(config)
            print("✓ Conversion successful with validation")
            if w:
                print(f"  Warnings ({len(w)}):")
                for warning in w:
                    print(f"    - {warning.message}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    print("=" * 70)
    print("Validation examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    test_validation()

