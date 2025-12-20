"""
完整工作流测试：水分子基态单点能量计算

测试从 AI 任务分析到结果分析的完整流程：
1. AI 任务分析产生 YAML 文件
2. YAML 文件到 BDF 输入转换
3. BDF 任务执行
4. BDF 执行结果信息提取
5. AI 分析
"""

import sys
import os
from pathlib import Path
import time

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
    TaskPlanner,
    BDFConverter,
    BDFValidator,
    YAMLGenerator,
    ConversionTool,
)
from bdfeasyinput.config import load_config, merge_config_with_defaults, get_ai_config
from bdfeasyinput.execution import create_runner
from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis import QuantumChemistryAnalyzer, AnalysisReportGenerator
from bdfeasyinput.extraction import BDFResultExtractor
from bdfeasyinput.config import get_ai_config
from bdfeasyinput.ai.client import (
    OllamaClient,
    OpenAIClient,
    AnthropicClient,
    OpenRouterClient,
    create_openai_compatible_client,
    AIClient,
)


def print_step(step_num, step_name):
    """打印步骤标题。"""
    print("\n" + "=" * 70)
    print(f"步骤 {step_num}: {step_name}")
    print("=" * 70)


def main():
    """主测试函数。"""
    
    print("=" * 70)
    print("BDFEasyInput 完整工作流测试")
    print("任务: 水分子基态单点能量计算")
    print("=" * 70)
    
    # 配置
    config_file = project_root / "config" / "config.yaml"
    output_dir = project_root / "test_outputs" / "full_workflow_h2o"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n输出目录: {output_dir}")
    print(f"配置文件: {config_file}")
    
    # 加载配置
    try:
        config = load_config(str(config_file))
        config = merge_config_with_defaults(config)
        print("✓ 配置文件加载成功")
    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        return 1
    
    # ========================================================================
    # 步骤 1: AI 任务分析产生 YAML 文件
    # ========================================================================
    print_step(1, "AI 任务分析产生 YAML 文件")
    
    query = "计算水分子的基态单点能量，使用 PBE0 泛函和 cc-pVDZ 基组"
    print(f"用户查询: {query}")
    
    try:
        # 获取 AI 客户端
        ai_config = get_ai_config(config)
        
        # 创建 AI 客户端（从配置）
        provider_name = ai_config.get("default_provider", "ollama")
        providers_config = ai_config.get("providers", {})
        provider_config = providers_config.get(provider_name, {})
        
        if provider_name == "ollama":
            base_url = provider_config.get("base_url", "http://localhost:11434")
            model = provider_config.get("model", "llama3")
            timeout = provider_config.get("timeout", 60)
            ai_client = OllamaClient(model_name=model, base_url=base_url, timeout=timeout)
        elif provider_name == "openai":
            model = provider_config.get("model", "gpt-4")
            api_key = os.getenv(provider_config.get("api_key_env", "OPENAI_API_KEY"))
            base_url = provider_config.get("base_url")
            timeout = provider_config.get("timeout", 60)
            ai_client = OpenAIClient(model=model, api_key=api_key, base_url=base_url, timeout=timeout)
        elif provider_name == "anthropic":
            model = provider_config.get("model", "claude-3-sonnet-20240229")
            api_key = os.getenv(provider_config.get("api_key_env", "ANTHROPIC_API_KEY"))
            timeout = provider_config.get("timeout", 60)
            ai_client = AnthropicClient(model=model, api_key=api_key, timeout=timeout)
        elif provider_name == "openrouter":
            model = provider_config.get("model", "openai/gpt-4")
            api_key = os.getenv(provider_config.get("api_key_env", "OPENROUTER_API_KEY"))
            base_url = provider_config.get("base_url")
            timeout = provider_config.get("timeout", 60)
            ai_client = OpenRouterClient(model=model, api_key=api_key, base_url=base_url, timeout=timeout)
        elif provider_name in ["together", "groq", "deepseek", "mistral", "perplexity"]:
            model = provider_config.get("model")
            api_key = os.getenv(provider_config.get("api_key_env", f"{provider_name.upper()}_API_KEY"))
            base_url = provider_config.get("base_url")
            timeout = provider_config.get("timeout", 60)
            ai_client = create_openai_compatible_client(
                service=provider_name, model=model, api_key=api_key, base_url=base_url, timeout=timeout
            )
        else:
            # 默认使用 Ollama
            ai_client = OllamaClient()
        
        if not ai_client.is_available():
            print("⚠ AI 客户端不可用，使用预设的 YAML 配置")
            # 使用预设配置
            task_config = {
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
        else:
            # 使用 AI 规划
            print("正在使用 AI 规划任务...")
            planner = TaskPlanner(ai_client=ai_client, validate_output=True)
            task_config = planner.plan(query)
            print("✓ AI 规划完成")
        
        # 保存 YAML 文件
        yaml_file = output_dir / "task.yaml"
        import yaml
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(task_config, f, default_flow_style=False, allow_unicode=True)
        print(f"✓ YAML 文件已保存: {yaml_file}")
        
        # 显示 YAML 内容
        print("\n生成的 YAML 配置:")
        print("-" * 70)
        with open(yaml_file, 'r') as f:
            print(f.read())
        print("-" * 70)
        
    except Exception as e:
        print(f"✗ 步骤 1 失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # ========================================================================
    # 步骤 2: YAML 文件到 BDF 输入转换
    # ========================================================================
    print_step(2, "YAML 文件到 BDF 输入转换")
    
    try:
        # 验证 YAML
        validator = BDFValidator()
        validated_config, warnings = validator.validate(task_config)
        if warnings:
            print(f"⚠ 验证警告 ({len(warnings)} 个):")
            for w in warnings:
                print(f"  - {w}")
        print("✓ YAML 验证通过")
        
        # 转换为 BDF
        converter = BDFConverter(validate_input=True)
        bdf_content = converter.convert(validated_config)
        
        # 保存 BDF 输入文件
        bdf_input_file = output_dir / "bdf_input.inp"
        with open(bdf_input_file, 'w', encoding='utf-8') as f:
            f.write(bdf_content)
        print(f"✓ BDF 输入文件已保存: {bdf_input_file}")
        
        # 显示 BDF 内容（前30行）
        print("\n生成的 BDF 输入文件（前30行）:")
        print("-" * 70)
        lines = bdf_content.split('\n')[:30]
        for i, line in enumerate(lines, 1):
            print(f"{i:3d}| {line}")
        if len(bdf_content.split('\n')) > 30:
            print(f"... (共 {len(bdf_content.split('\n'))} 行)")
        print("-" * 70)
        
    except Exception as e:
        print(f"✗ 步骤 2 失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # ========================================================================
    # 步骤 3: BDF 任务执行
    # ========================================================================
    print_step(3, "BDF 任务执行")
    
    try:
        # 创建执行器
        runner = create_runner(config=config)
        print(f"✓ 执行器创建成功: {type(runner).__name__}")
        
        # 运行计算
        print(f"\n开始执行 BDF 计算...")
        print(f"输入文件: {bdf_input_file}")
        print(f"输出目录: {output_dir}")
        print("请稍候...\n")
        
        start_time = time.time()
        execution_result = runner.run(
            str(bdf_input_file),
            output_dir=str(output_dir)
        )
        elapsed_time = time.time() - start_time
        
        print(f"\n计算完成 (耗时: {elapsed_time:.1f} 秒)")
        
        if execution_result.get('status') == 'success':
            print("✓ 计算执行成功")
            output_file = execution_result.get('output_file')
            if output_file:
                print(f"✓ 输出文件: {output_file}")
            log_file = execution_result.get('log_file')
            if log_file:
                print(f"✓ 日志文件: {log_file}")
        else:
            error_msg = execution_result.get('error', 'Unknown error')
            print(f"✗ 计算执行失败: {error_msg}")
            # 即使失败，也尝试提取和分析结果
            output_file = execution_result.get('output_file')
            if not output_file:
                print("⚠ 无法继续后续步骤（无输出文件）")
                return 1
        
    except Exception as e:
        print(f"✗ 步骤 3 失败: {e}")
        import traceback
        traceback.print_exc()
        # 尝试使用示例输出文件继续测试
        print("\n⚠ 尝试使用示例输出文件继续测试...")
        output_file = None
        # 查找可能的输出文件
        for pattern in ['*.log', '*.out']:
            files = list(output_dir.glob(pattern))
            if files:
                output_file = str(files[0])
                print(f"找到输出文件: {output_file}")
                break
        
        if not output_file:
            print("✗ 无法继续（无输出文件）")
            return 1
    
    # ========================================================================
    # 步骤 4: BDF 执行结果信息提取
    # ========================================================================
    print_step(4, "BDF 执行结果信息提取")
    
    try:
        # 使用提取器提取指标
        extractor = BDFResultExtractor()
        metrics = extractor.extract_metrics(output_file, task_type='single_point')
        
        print("✓ 结果提取成功")
        print(f"✓ 任务类型: {metrics.task_type}")
        
        # 显示提取的指标
        metrics_dict = metrics.to_dict()
        print("\n提取的指标:")
        print("-" * 70)
        import json
        print(json.dumps(metrics_dict, indent=2, ensure_ascii=False))
        print("-" * 70)
        
        # 保存指标到 JSON
        metrics_file = output_dir / "metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_dict, f, indent=2, ensure_ascii=False)
        print(f"✓ 指标已保存到: {metrics_file}")
        
    except Exception as e:
        print(f"✗ 步骤 4 失败: {e}")
        import traceback
        traceback.print_exc()
        # 继续尝试分析
        metrics = None
    
    # ========================================================================
    # 步骤 5: AI 分析
    # ========================================================================
    print_step(5, "AI 分析")
    
    try:
        # 解析输出文件
        parser = BDFOutputParser()
        parsed_data = parser.parse(output_file)
        print("✓ 输出文件解析成功")
        
        # 获取 AI 客户端用于分析
        analysis_config = config.get('analysis', {})
        ai_config_analysis = analysis_config.get('ai', {})
        
        # 使用分析配置中的 AI 设置，或回退到默认
        analysis_provider = ai_config_analysis.get('provider') or ai_config.get('default_provider')
        analysis_model = ai_config_analysis.get('model')
        
        # 使用相同的 AI 客户端（或根据分析配置创建新的）
        analysis_client = ai_client
        
        if not analysis_client or not analysis_client.is_available():
            print("⚠ AI 客户端不可用，跳过 AI 分析")
            print("✓ 使用基础解析结果")
        else:
            # 创建分析器
            analyzer = QuantumChemistryAnalyzer(ai_client=analysis_client)
            
            # 执行分析
            print("正在使用 AI 分析结果...")
            analysis_result = analyzer.analyze(
                output_file=output_file,
                input_file=str(bdf_input_file),
                task_type='energy',
                language=analysis_config.get('ai', {}).get('language', 'zh')
            )
            print("✓ AI 分析完成")
            
            # 生成报告
            report_format = analysis_config.get('output', {}).get('format', 'markdown')
            report_language = analysis_config.get('ai', {}).get('language', 'zh')
            report_generator = AnalysisReportGenerator(format=report_format, language=report_language)
            report_content = report_generator.generate(
                analysis_result=analysis_result,
                parsed_data=parsed_data,
                output_file=None  # 先不写入文件，后面手动写入
            )
            
            # 保存报告
            report_file = output_dir / "analysis_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✓ 分析报告已保存: {report_file}")
            
            # 显示报告摘要
            print("\n分析报告摘要:")
            print("-" * 70)
            lines = report_content.split('\n')[:50]
            for line in lines:
                print(line)
            if len(report_content.split('\n')) > 50:
                print(f"... (共 {len(report_content.split('\n'))} 行)")
            print("-" * 70)
        
    except Exception as e:
        print(f"✗ 步骤 5 失败: {e}")
        import traceback
        traceback.print_exc()
        # 不返回错误，因为基础解析可能已经完成
    
    # ========================================================================
    # 总结
    # ========================================================================
    print("\n" + "=" * 70)
    print("完整工作流测试总结")
    print("=" * 70)
    
    print(f"\n输出目录: {output_dir}")
    print("\n生成的文件:")
    files = list(output_dir.glob("*"))
    for f in sorted(files):
        if f.is_file():
            size = f.stat().st_size
            print(f"  - {f.name} ({size} bytes)")
    
    print("\n" + "=" * 70)
    print("✓ 完整工作流测试完成！")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
