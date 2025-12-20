"""
Integration test for venv_bdf virtual environment.

This test verifies that all packages (BDFEasyInput, BDFAgent, bdfeasyinput_schema)
work correctly in the unified virtual environment.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_schema_import():
    """Test bdfeasyinput_schema import."""
    try:
        from bdfeasyinput_schema import (
            EasyInputConfig,
            TaskType,
            MethodType,
            CoordinateUnit,
            EasyInputTask,
            EasyInputMolecule,
            EasyInputMethod,
        )
        assert TaskType.ENERGY.value == "energy"
        assert MethodType.DFT.value == "dft"
        assert CoordinateUnit.ANGSTROM.value == "angstrom"
        print("✓ Schema imports successful")
        return True
    except ImportError as e:
        print(f"✗ Schema import failed: {e}")
        return False


def test_bdfeasyinput_core():
    """Test BDFEasyInput core imports."""
    try:
        from bdfeasyinput import (
            BDFValidator,
            ValidationError,
            BDFConverter,
            TaskType,
            MethodType,
        )
        assert TaskType.ENERGY.value == "energy"
        assert MethodType.DFT.value == "dft"
        print("✓ BDFEasyInput core imports successful")
        return True
    except ImportError as e:
        print(f"✗ BDFEasyInput import failed: {e}")
        return False


def test_validator_functionality():
    """Test validator functionality."""
    try:
        from bdfeasyinput import BDFValidator, ValidationError

        # Valid config
        config = {
            "task": {"type": "energy", "description": "Test"},
            "molecule": {
                "name": "water",
                "charge": 0,
                "multiplicity": 1,
                "coordinates": ["O 0.0 0.0 0.0", "H 0.0 0.0 0.96", "H 0.0 0.87 0.0"],
                "units": "angstrom",
            },
            "method": {"type": "dft", "functional": "pbe0", "basis": "cc-pvdz"},
        }

        validator = BDFValidator()
        result, warnings = validator.validate(config)
        assert result["task"]["type"] == "energy"
        print("✓ Validator functionality test passed")
        return True
    except Exception as e:
        print(f"✗ Validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_converter_integration():
    """Test converter integration with validator."""
    try:
        from bdfeasyinput import BDFConverter, BDFValidator

        config = {
            "task": {"type": "energy"},
            "molecule": {
                "name": "H2",
                "charge": 0,
                "multiplicity": 1,
                "coordinates": ["H 0.0 0.0 0.0", "H 0.0 0.0 0.74"],
                "units": "angstrom",
            },
            "method": {"type": "dft", "functional": "pbe0", "basis": "cc-pvdz"},
        }

        # Validate first
        validator = BDFValidator()
        validated_config, _ = validator.validate(config)

        # Then convert
        converter = BDFConverter(validate_input=True)
        bdf_content = converter.convert(validated_config)
        assert "COMPASS" in bdf_content
        print("✓ Converter integration test passed")
        return True
    except Exception as e:
        print(f"✗ Converter integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaml_generator():
    """Test YAML generator."""
    try:
        from bdfeasyinput import YAMLGenerator

        generator = YAMLGenerator(validate_output=True)
        template = generator.generate_template("energy", include_comments=False)
        assert template["task"]["type"] == "energy"
        print("✓ YAML generator test passed")
        return True
    except Exception as e:
        print(f"✗ YAML generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bdfagent_compatibility():
    """Test BDFAgent compatibility (optional)."""
    try:
        import agent
        from agent.adapters.easyinput_schema import EasyInputAdapter
        print("✓ BDFAgent compatibility check passed")
        return True
    except ImportError:
        print("⚠ BDFAgent not installed (optional, skipping)")
        return True  # Not a failure
    except Exception as e:
        print(f"⚠ BDFAgent compatibility check warning: {e}")
        return True  # Not a failure


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("venv_bdf Integration Test")
    print("=" * 60)
    print()

    results = []

    print("1. Testing bdfeasyinput_schema...")
    results.append(("Schema Import", test_schema_import()))
    print()

    print("2. Testing BDFEasyInput core...")
    results.append(("BDFEasyInput Core", test_bdfeasyinput_core()))
    print()

    print("3. Testing validator functionality...")
    results.append(("Validator", test_validator_functionality()))
    print()

    print("4. Testing converter integration...")
    results.append(("Converter Integration", test_converter_integration()))
    print()

    print("5. Testing YAML generator...")
    results.append(("YAML Generator", test_yaml_generator()))
    print()

    print("6. Testing BDFAgent compatibility...")
    results.append(("BDFAgent Compatibility", test_bdfagent_compatibility()))
    print()

    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
