"""
结构优化测试

测试从 YAML 文件进行结构优化的完整流程
"""

import sys
from pathlib import Path
from bdfeasyinput import BDFConverter, load_config
from bdfeasyinput.execution import create_runner


def main():
    """测试结构优化"""
    
    print("=" * 70)
    print("BDFEasyInput 结构优化测试")
    print("=" * 70)
    print()
    
    # 创建简单的结构优化 YAML 配置
    yaml_content = """# 水分子结构优化示例

task:
  type: optimize
  description: "H2O geometry optimization with B3LYP/cc-pVDZ"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000  0.0000  0.1173
    - H  0.0000  0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  geometry_optimization:
    solver: 1  # BDF native optimizer
    max_cycle: 50
    tol_grad: 1e-4
    tol_ene: 1e-6
"""
    
    # 保存 YAML 文件
    yaml_file = "examples/h2o_opt_test.yaml"
    yaml_path = Path(yaml_file)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"1. 创建 YAML 输入文件: {yaml_file}")
    print(f"   ✓ 文件已创建")
    print()
    
    # 转换 YAML 到 BDF
    print("2. 转换 YAML 到 BDF 输入...")
    try:
        converter = BDFConverter()
        
        # 输出文件路径
        output_dir = Path("/Users/bsuo/check/bdf")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        bdf_input_file = output_dir / "h2o_opt.inp"
        
        # 转换
        bdf_content = converter.convert_file(yaml_file, str(bdf_input_file))
        
        print(f"   ✓ BDF 输入文件已生成: {bdf_input_file}")
        print(f"   文件大小: {bdf_input_file.stat().st_size} 字节")
        print()
        
        # 显示 BDF 输入文件内容
        print("   BDF 输入文件内容:")
        print("   " + "-" * 66)
        with open(bdf_input_file, 'r') as f:
            content = f.read()
            print(content)
        print("   " + "-" * 66)
        print()
        
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 加载配置
    print("3. 加载配置文件...")
    try:
        config = load_config()
        print(f"   ✓ 配置文件加载成功")
        print()
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        return 1
    
    # 创建执行器
    print("4. 创建执行器...")
    try:
        runner = create_runner(config=config)
        print(f"   ✓ 执行器创建成功: {type(runner).__name__}")
        print()
    except Exception as e:
        print(f"✗ 创建执行器失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 运行结构优化
    print("5. 运行结构优化计算...")
    print(f"   输入文件: {bdf_input_file}")
    print("   注意: 结构优化可能需要较长时间，请耐心等待...")
    print()
    
    try:
        result = runner.run(str(bdf_input_file), timeout=3600)
        
        print("6. 计算结果:")
        print(f"   状态: {result['status']}")
        print(f"   退出码: {result['exit_code']}")
        print(f"   执行时间: {result['execution_time']:.2f} 秒")
        print()
        
        # 输出文件信息
        output_file = result.get('output_file')
        error_file = result.get('error_file')
        
        if output_file:
            output_path = Path(output_file)
            if output_path.exists():
                size = output_path.stat().st_size
                print(f"   ✓ 输出文件: {output_file}")
                print(f"     文件大小: {size:,} 字节")
                
                # 检查优化是否成功
                with open(output_path, 'r') as f:
                    content = f.read()
                    if "normal termination" in content.lower():
                        print(f"     ✓ 计算正常终止")
                    
                    # 查找优化相关信息
                    if "optimization converged" in content.lower() or "converged" in content.lower():
                        print(f"     ✓ 结构优化已收敛")
                    
                    # 查找最终能量
                    lines = content.split('\n')
                    for line in reversed(lines[-100:]):
                        if "RKS=" in line or "RHF=" in line or "UHF=" in line:
                            print(f"     最终能量: {line.strip()[:100]}")
                            break
                    
                    # 查找优化后的几何结构
                    if "optimized geometry" in content.lower() or "final geometry" in content.lower():
                        print(f"     ✓ 优化后的几何结构已生成")
            else:
                print(f"   ⚠️  输出文件不存在: {output_file}")
        
        if error_file:
            error_path = Path(error_file)
            if error_path.exists():
                size = error_path.stat().st_size
                if size == 0:
                    print(f"   ✓ 错误文件: {error_file} (0 字节，无错误)")
                else:
                    print(f"   ⚠️  错误文件: {error_file} ({size} 字节)")
                    with open(error_path, 'r') as f:
                        error_lines = f.readlines()[:10]
                        print("     错误内容（前10行）:")
                        for line in error_lines:
                            print(f"     {line.rstrip()}")
        
        # 检查优化后的几何结构文件
        optgeom_file = output_dir / "h2o_opt.optgeom"
        if optgeom_file.exists():
            print(f"   ✓ 优化后的几何结构文件: {optgeom_file}")
            size = optgeom_file.stat().st_size
            print(f"     文件大小: {size} 字节")
            
            # 显示优化后的坐标（如果有）
            if size > 0:
                with open(optgeom_file, 'r') as f:
                    geom_content = f.read()
                    if geom_content.strip():
                        print("     优化后的坐标:")
                        lines = geom_content.strip().split('\n')[:10]
                        for line in lines:
                            print(f"     {line}")
        
        print()
        
        # 检查执行状态
        if result['status'] == 'success':
            print("   ✅ 结构优化计算成功完成！")
            print()
            print("=" * 70)
            print("结构优化测试成功！")
            print("=" * 70)
            return 0
        elif result['status'] == 'timeout':
            print("   ✗ 计算超时")
            return 1
        else:
            print("   ✗ 计算失败")
            if result.get('stderr'):
                stderr = result['stderr']
                if stderr:
                    print(f"   错误信息（前500字符）:")
                    print(f"   {stderr[:500]}")
            return 1
        
    except Exception as e:
        print(f"✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

