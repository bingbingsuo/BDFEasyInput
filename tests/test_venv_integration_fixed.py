"""
Integration test for venv_bdf virtual environment (Fixed version).

This test verifies that all packages (BDFEasyInput, BDFAgent, bdfeasyinput_schema)
work correctly in the unified virtual environment.

Note: This script fixes the sys.path issue when running from BDFEasyInput directory.
"""

import sys
import os
from pathlib import Path

# Fix sys.path for editable installs
# When running from BDFEasyInput directory, we need to ensure the parent directory
# is in sys.path for bdfeasyinput_schema to be found

# Get current working directory
cwd = Path(os.getcwd()).resolve()

# Find the bdf root directory (parent of BDFEasyInput or current if at root)
if cwd.name == 'BDFEasyInput':
    bdf_root = str(cwd.parent)
elif (cwd / 'BDFEasyInput').exists():
    bdf_root = str(cwd)
else:
    # Try to find it by going up
    bdf_root = None
    for parent in cwd.parents:
        if (parent / 'BDFEasyInput').exists() and (parent / 'bdfeasyinput_schema').exists():
            bdf_root = str(parent)
            break

# Fix sys.path[0] which is set to current directory when running script
if sys.path and sys.path[0]:
    path0_str = sys.path[0]
    # Remove empty string or current directory
    if not path0_str or path0_str == '.':
        sys.path.pop(0)
    else:
        path0 = Path(path0_str).resolve()
        # If sys.path[0] is a script directory inside BDFEasyInput, we may need to adjust
        if path0.name == 'BDFEasyInput' or (path0.parent.name == 'BDFEasyInput' and path0.name == 'tests'):
            # Keep it but ensure parent is also in path
            pass

# Ensure bdf root directory is in path for editable installs
if bdf_root and bdf_root not in sys.path:
    sys.path.insert(0, bdf_root)

# Also try to manually install the editable finder if needed
try:
    import __editable___bdfeasyinput_schema_0_1_0_finder
    __editable___bdfeasyinput_schema_0_1_0_finder.install()
except (ImportError, AttributeError):
    pass  # Finder may not be needed or already installed

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
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
        import traceback
        traceback.print_exc()
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
        assert result["molecule"]["name"] == "water"
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
        assert "XUANYUAN" in bdf_content
        assert "SCF" in bdf_content
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


def test_error_handling():
    """Test error handling."""
    try:
        from bdfeasyinput import BDFValidator, ValidationError

        validator = BDFValidator()
        try:
            validator.validate({"invalid": "config"})
            print("✗ Error handling test failed: should have raised ValidationError")
            return False
        except ValidationError:
            print("✓ Error handling test passed")
            return True
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
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
    print("venv_bdf Integration Test (Fixed)")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"sys.path[0:3]: {sys.path[0:3]}")
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

    print("6. Testing error handling...")
    results.append(("Error Handling", test_error_handling()))
    print()

    print("7. Testing BDFAgent compatibility...")
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
