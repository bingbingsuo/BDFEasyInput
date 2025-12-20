"""
BDFEasyInput 与 bdfeasyinput_schema 集成功能测试

生成多个计算任务的 YAML 文件并转换为 BDF 输入，供人工审查。
"""

import sys
import os
from pathlib import Path

# Fix sys.path for editable installs
cwd = Path(os.getcwd()).resolve()
if cwd.name == 'BDFEasyInput':
    if sys.path and sys.path[0]:
        path0 = Path(sys.path[0]).resolve()
        if path0 == cwd or path0.name == 'BDFEasyInput':
            sys.path.pop(0)
    parent_dir = str(cwd.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from bdfeasyinput import (
    YAMLGenerator,
    ConversionTool,
    BDFValidator,
    TaskType,
    MethodType,
)
from bdfeasyinput_schema import EasyInputConfig


def generate_test_cases():
    """生成测试用例配置。"""
    
    test_cases = []
    
    # 测试用例 1: 水分子单点能计算 (DFT)
    test_cases.append({
        'name': 'h2o_energy_pbe0',
        'description': 'Water single point energy calculation with PBE0',
        'config': {
            'task': {
                'type': 'energy',
                'description': 'Water single point energy calculation',
                'title': 'H2O Energy PBE0'
            },
            'molecule': {
                'name': 'Water',
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'O  0.0000  0.0000  0.1173',
                    'H  0.0000  0.7572 -0.4692',
                    'H  0.0000 -0.7572 -0.4692'
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
        }
    })
    
    # 测试用例 2: 水分子几何优化
    test_cases.append({
        'name': 'h2o_optimize_b3lyp',
        'description': 'Water geometry optimization with B3LYP',
        'config': {
            'task': {
                'type': 'optimize',
                'description': 'Water geometry optimization',
                'title': 'H2O Optimize B3LYP'
            },
            'molecule': {
                'name': 'Water',
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'O  0.0000  0.0000  0.1173',
                    'H  0.0000  0.7572 -0.4692',
                    'H  0.0000 -0.7572 -0.4692'
                ],
                'units': 'angstrom'
            },
            'method': {
                'type': 'dft',
                'functional': 'b3lyp',
                'basis': '6-31g*'
            },
            'settings': {
                'scf': {
                    'convergence': 1e-6,
                    'max_iterations': 100
                },
                'geometry_optimization': {
                    'solver': 1,
                    'max_cycle': 50,
                    'tol_grad': 1e-4,
                    'tol_ene': 1e-6
                }
            }
        }
    })
    
    # 测试用例 3: 水分子频率计算
    test_cases.append({
        'name': 'h2o_frequency_pbe0',
        'description': 'Water frequency calculation with PBE0',
        'config': {
            'task': {
                'type': 'frequency',
                'description': 'Water frequency calculation',
                'title': 'H2O Frequency PBE0'
            },
            'molecule': {
                'name': 'Water',
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'O  0.0000  0.0000  0.1173',
                    'H  0.0000  0.7572 -0.4692',
                    'H  0.0000 -0.7572 -0.4692'
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
        }
    })
    
    # 测试用例 4: 水分子 TDDFT 激发态计算
    test_cases.append({
        'name': 'h2o_tddft_pbe0',
        'description': 'Water TDDFT excited state calculation',
        'config': {
            'task': {
                'type': 'tddft',
                'description': 'Water TDDFT excited state calculation',
                'title': 'H2O TDDFT PBE0'
            },
            'molecule': {
                'name': 'Water',
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'O  0.0000  0.0000  0.1173',
                    'H  0.0000  0.7572 -0.4692',
                    'H  0.0000 -0.7572 -0.4692'
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
                    'spin': 'singlet',
                    'nstates': 10,
                    'method': 'tddft',
                    'tda': False
                }
            }
        }
    })
    
    # 测试用例 5: 甲醛分子单点能 (HF)
    test_cases.append({
        'name': 'ch2o_energy_hf',
        'description': 'Formaldehyde single point energy with HF',
        'config': {
            'task': {
                'type': 'energy',
                'description': 'Formaldehyde single point energy',
                'title': 'CH2O Energy HF'
            },
            'molecule': {
                'name': 'Formaldehyde',
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'C  0.0000  0.0000  0.0000',
                    'O  0.0000  0.0000  1.2030',
                    'H  0.0000  0.9420 -0.5200',
                    'H  0.0000 -0.9420 -0.5200'
                ],
                'units': 'angstrom'
            },
            'method': {
                'type': 'hf',
                'basis': '6-31g*'
            },
            'settings': {
                'scf': {
                    'convergence': 1e-6,
                    'max_iterations': 100
                }
            }
        }
    })
    
    # 测试用例 6: 苯分子优化 (带对称性)
    test_cases.append({
        'name': 'c6h6_optimize_pbe0',
        'description': 'Benzene geometry optimization with PBE0',
        'config': {
            'task': {
                'type': 'optimize',
                'description': 'Benzene geometry optimization',
                'title': 'C6H6 Optimize PBE0'
            },
            'molecule': {
                'name': 'Benzene',
                'charge': 0,
                'multiplicity': 1,
                'coordinates': [
                    'C  0.0000  1.3970  0.0000',
                    'C  1.2112  0.6985  0.0000',
                    'C  1.2112 -0.6985  0.0000',
                    'C  0.0000 -1.3970  0.0000',
                    'C -1.2112 -0.6985  0.0000',
                    'C -1.2112  0.6985  0.0000',
                    'H  0.0000  2.4810  0.0000',
                    'H  2.1500  1.2405  0.0000',
                    'H  2.1500 -1.2405  0.0000',
                    'H  0.0000 -2.4810  0.0000',
                    'H -2.1500 -1.2405  0.0000',
                    'H -2.1500  1.2405  0.0000'
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
                    'solver': 1,
                    'max_cycle': 50
                }
            }
        }
    })
    
    return test_cases


def main():
    """主测试函数。"""
    
    print("=" * 70)
    print("BDFEasyInput 与 bdfeasyinput_schema 集成功能测试")
    print("=" * 70)
    print()
    
    # 创建输出目录
    output_dir = Path(__file__).parent.parent / "test_outputs" / "schema_integration"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"输出目录: {output_dir}")
    print()
    
    # 初始化工具
    generator = YAMLGenerator(validate_output=True)
    converter = ConversionTool(validate_input=True)
    validator = BDFValidator()
    
    # 生成测试用例
    test_cases = generate_test_cases()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        name = test_case['name']
        description = test_case['description']
        config = test_case['config']
        
        print(f"{i}. {name}")
        print(f"   描述: {description}")
        
        try:
            # 验证配置
            validated_config, warnings = validator.validate(config)
            if warnings:
                print(f"   ⚠ 警告: {len(warnings)} 个")
                for w in warnings:
                    print(f"      - {w}")
            
            # 保存 YAML 文件
            yaml_file = output_dir / f"{name}.yaml"
            generator.save_yaml(validated_config, yaml_file)
            print(f"   ✓ YAML 文件: {yaml_file}")
            
            # 转换为 BDF 输入
            bdf_file = output_dir / f"{name}.inp"
            converter.convert_file(yaml_file, bdf_file, overwrite=True)
            print(f"   ✓ BDF 文件: {bdf_file}")
            
            # 检查文件大小
            yaml_size = yaml_file.stat().st_size
            bdf_size = bdf_file.stat().st_size
            print(f"   ✓ 文件大小: YAML={yaml_size} bytes, BDF={bdf_size} bytes")
            
            results.append({
                'name': name,
                'status': 'success',
                'yaml_file': str(yaml_file),
                'bdf_file': str(bdf_file),
                'warnings': len(warnings)
            })
            
        except Exception as e:
            print(f"   ✗ 失败: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'name': name,
                'status': 'failed',
                'error': str(e)
            })
        
        print()
    
    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count
    
    print(f"总测试数: {len(results)}")
    print(f"成功: {success_count}")
    if failed_count > 0:
        print(f"失败: {failed_count}")
    
    print()
    print("生成的文件:")
    for r in results:
        if r['status'] == 'success':
            print(f"  ✓ {r['name']}")
            print(f"    YAML: {r['yaml_file']}")
            print(f"    BDF:  {r['bdf_file']}")
            if r.get('warnings', 0) > 0:
                print(f"    ⚠ 警告: {r['warnings']} 个")
        else:
            print(f"  ✗ {r['name']}: {r.get('error', 'Unknown error')}")
    
    print()
    print("=" * 70)
    print(f"所有文件已生成到: {output_dir}")
    print("请人工审查生成的 YAML 和 BDF 文件")
    print("=" * 70)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
