"""
Example: YAML Generation and Conversion

This example demonstrates how to use the YAML generation and conversion tools.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bdfeasyinput.yaml_generator import YAMLGenerator, generate_yaml_template
from bdfeasyinput.conversion_tool import ConversionTool


def example_1_generate_template():
    """Example 1: Generate YAML template."""
    print("=" * 60)
    print("Example 1: Generate YAML Template")
    print("=" * 60)
    
    generator = YAMLGenerator(validate_output=False)
    
    # Generate energy calculation template
    template = generator.generate_template('energy', include_comments=True)
    
    # Save to file
    output_path = Path(__file__).parent / 'generated_energy_template.yaml'
    generator.save_yaml(template, output_path)
    
    print(f"✓ Template saved to: {output_path}")
    print()


def example_2_generate_from_template():
    """Example 2: Generate YAML from template parameters."""
    print("=" * 60)
    print("Example 2: Generate YAML from Template Parameters")
    print("=" * 60)
    
    generator = YAMLGenerator(validate_output=False)
    
    # Generate configuration
    config = generator.generate_from_template(
        task_type='energy',
        molecule={
            'name': 'Water',
            'charge': 0,
            'multiplicity': 1,
            'coordinates': [
                'O  0.0000 0.0000 0.1173',
                'H  0.0000 0.7572 -0.4692',
                'H  0.0000 -0.7572 -0.4692'
            ],
            'units': 'angstrom'
        },
        method={
            'type': 'dft',
            'functional': 'pbe0',
            'basis': 'cc-pvdz'
        },
        settings={
            'scf': {
                'convergence': 1e-6,
                'max_iterations': 100
            }
        },
        description='Water single point energy calculation'
    )
    
    # Save to file
    output_path = Path(__file__).parent / 'generated_water_energy.yaml'
    generator.save_yaml(config, output_path)
    
    print(f"✓ Configuration saved to: {output_path}")
    print()


def example_3_convert_yaml():
    """Example 3: Convert YAML to BDF input."""
    print("=" * 60)
    print("Example 3: Convert YAML to BDF Input")
    print("=" * 60)
    
    # First, generate a YAML file (using example 2)
    generator = YAMLGenerator(validate_output=False)
    config = generator.generate_from_template(
        task_type='energy',
        molecule={
            'charge': 0,
            'multiplicity': 1,
            'coordinates': [
                'O  0.0000 0.0000 0.1173',
                'H  0.0000 0.7572 -0.4692',
                'H  0.0000 -0.7572 -0.4692'
            ],
            'units': 'angstrom'
        },
        method={
            'type': 'dft',
            'functional': 'pbe0',
            'basis': 'cc-pvdz'
        }
    )
    
    yaml_path = Path(__file__).parent / 'example_water.yaml'
    generator.save_yaml(config, yaml_path)
    print(f"✓ Created YAML file: {yaml_path}")
    
    # Convert to BDF
    converter = ConversionTool(validate_input=False)
    bdf_path = converter.convert_file(yaml_path, overwrite=True)
    
    print(f"✓ BDF input file generated: {bdf_path}")
    
    # Preview first few lines
    preview, _ = converter.preview(yaml_path, max_lines=20)
    print("\nPreview of BDF input (first 20 lines):")
    print("-" * 60)
    print(preview)
    print()


def example_4_batch_operations():
    """Example 4: Batch operations."""
    print("=" * 60)
    print("Example 4: Batch Operations")
    print("=" * 60)
    
    generator = YAMLGenerator(validate_output=False)
    converter = ConversionTool(validate_input=False)
    
    # Generate multiple YAML files
    task_types = ['energy', 'optimize', 'frequency']
    yaml_files = []
    
    for task_type in task_types:
        config = generator.generate_from_template(
            task_type=task_type,
            molecule={
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'O  0.0000 0.0000 0.1173',
                    'H  0.0000 0.7572 -0.4692',
                    'H  0.0000 -0.7572 -0.4692'
                ],
                'units': 'angstrom'
            },
            method={
                'type': 'dft',
                'functional': 'pbe0',
                'basis': 'cc-pvdz'
            }
        )
        
        yaml_path = Path(__file__).parent / f'example_{task_type}.yaml'
        generator.save_yaml(config, yaml_path)
        yaml_files.append(yaml_path)
        print(f"✓ Generated: {yaml_path}")
    
    # Batch convert
    output_dir = Path(__file__).parent / 'bdf_outputs'
    results = converter.batch_convert(yaml_files, output_dir=output_dir, overwrite=True)
    
    print(f"\n✓ Batch conversion complete:")
    for yaml_file, result in results.items():
        if isinstance(result, Path):
            print(f"  ✓ {yaml_file} -> {result}")
        else:
            print(f"  ✗ {yaml_file}: {result}")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("YAML Generation and Conversion Examples")
    print("=" * 60 + "\n")
    
    try:
        example_1_generate_template()
        example_2_generate_from_template()
        example_3_convert_yaml()
        example_4_batch_operations()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
