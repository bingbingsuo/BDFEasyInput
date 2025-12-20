"""
Test script for YAML generation and conversion functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from bdfeasyinput.yaml_generator import YAMLGenerator, generate_yaml_template
    from bdfeasyinput.conversion_tool import ConversionTool
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Note: This may be due to missing dependencies (pyyaml, etc.)")
    sys.exit(1)


def test_template_generation():
    """Test YAML template generation."""
    print("\n1. Testing template generation...")
    
    try:
        generator = YAMLGenerator(validate_output=False)
        
        # Test all task types
        for task_type in ['energy', 'optimize', 'frequency', 'tddft']:
            template = generator.generate_template(task_type, include_comments=True)
            assert 'task' in template
            assert 'molecule' in template
            assert 'method' in template
            assert template['task']['type'] == task_type
            print(f"   ✓ Generated {task_type} template")
        
        print("   ✓ All templates generated successfully")
        return True
        
    except Exception as e:
        print(f"   ✗ Template generation failed: {e}")
        return False


def test_yaml_structure():
    """Test YAML structure generation."""
    print("\n2. Testing YAML structure generation...")
    
    try:
        generator = YAMLGenerator(validate_output=False)
        
        # Test from_template
        config = generator.generate_from_template(
            task_type='energy',
            molecule={
                'charge': 0,
                'multiplicity': 1,
                'coordinates': ['O 0.0 0.0 0.0', 'H 0.0 0.0 0.96'],
                'units': 'angstrom'
            },
            method={
                'type': 'dft',
                'functional': 'pbe0',
                'basis': 'cc-pvdz'
            }
        )
        
        assert config['task']['type'] == 'energy'
        assert config['molecule']['charge'] == 0
        assert config['method']['type'] == 'dft'
        print("   ✓ YAML structure generation successful")
        return True
        
    except Exception as e:
        print(f"   ✗ YAML structure generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversion_tool():
    """Test conversion tool initialization."""
    print("\n3. Testing conversion tool...")
    
    try:
        tool = ConversionTool(validate_input=False)
        assert tool.converter is not None
        assert tool.yaml_generator is not None
        print("   ✓ Conversion tool initialized successfully")
        return True
        
    except Exception as e:
        print(f"   ✗ Conversion tool initialization failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("YAML Generation and Conversion Tool Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Template Generation", test_template_generation()))
    results.append(("YAML Structure", test_yaml_structure()))
    results.append(("Conversion Tool", test_conversion_tool()))
    
    print("\n" + "=" * 60)
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
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
