"""
Command Line Interface for BDFEasyInput
"""

import sys
import os
import yaml
import click
from pathlib import Path
from typing import Optional

from .config import load_config, get_ai_config, merge_config_with_defaults
from .converter import BDFConverter
from .validator import BDFValidator, ValidationError
from .ai.parser.response_parser import parse_ai_response, AIResponseParseError
from .ai import TaskPlanner, PlanningError
from .ai.client import (
    OllamaClient, 
    OpenAIClient, 
    AnthropicClient, 
    AIClient,
    OpenRouterClient,
    create_openai_compatible_client,
)
from .yaml_generator import YAMLGenerator, generate_yaml_from_xyz, generate_yaml_template
from .conversion_tool import ConversionTool, convert_yaml_to_bdf, batch_convert_yaml


def get_ai_client_from_config(config_path: Optional[str] = None) -> AIClient:
    """
    Create an AI client from configuration.
    
    Args:
        config_path: Optional path to config file.
    
    Returns:
        Initialized AI client.
    
    Raises:
        click.ClickException: If client creation fails.
    """
    try:
        config = load_config(config_path)
        config = merge_config_with_defaults(config)
        ai_config = get_ai_config(config)
        
        if not ai_config.get("enabled", True):
            raise click.ClickException("AI features are disabled in configuration.")
        
        provider_name = ai_config.get("default_provider", "ollama")
        providers_config = ai_config.get("providers", {})
        provider_config = providers_config.get(provider_name, {})
        
        if not provider_config.get("enabled", True):
            raise click.ClickException(
                f"Provider '{provider_name}' is disabled in configuration."
            )
        
        defaults = ai_config.get("defaults", {})
        
        # Create client based on provider
        if provider_name == "ollama":
            base_url = provider_config.get("base_url", "http://localhost:11434")
            model = provider_config.get("model", "llama3")
            timeout = provider_config.get("timeout", 60)
            
            client = OllamaClient(
                model_name=model,
                base_url=base_url,
                timeout=timeout
            )
            
        elif provider_name == "openai":
            model = provider_config.get("model", "gpt-4")
            api_key = os.getenv(provider_config.get("api_key_env", "OPENAI_API_KEY"))
            base_url = provider_config.get("base_url")
            timeout = provider_config.get("timeout", 60)
            
            try:
                client = OpenAIClient(
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    timeout=timeout
                )
            except ImportError:
                raise click.ClickException(
                    "OpenAI package is not installed. "
                    "Install it with: pip install openai>=1.0.0"
                )
            except ValueError as e:
                raise click.ClickException(str(e))
            
        elif provider_name == "anthropic":
            model = provider_config.get("model", "claude-3-sonnet-20240229")
            api_key = os.getenv(provider_config.get("api_key_env", "ANTHROPIC_API_KEY"))
            timeout = provider_config.get("timeout", 60)
            
            try:
                client = AnthropicClient(
                    model=model,
                    api_key=api_key,
                    timeout=timeout
                )
            except ImportError:
                raise click.ClickException(
                    "Anthropic package is not installed. "
                    "Install it with: pip install anthropic>=0.3.0"
                )
            except ValueError as e:
                raise click.ClickException(str(e))
        
        elif provider_name == "openrouter":
            model = provider_config.get("model", "openai/gpt-4")
            api_key = os.getenv(provider_config.get("api_key_env", "OPENROUTER_API_KEY"))
            base_url = provider_config.get("base_url")
            timeout = provider_config.get("timeout", 60)
            
            try:
                client = OpenRouterClient(
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    timeout=timeout
                )
            except ImportError:
                raise click.ClickException(
                    "OpenAI package is not installed. "
                    "Install it with: pip install openai>=1.0.0"
                )
            except ValueError as e:
                raise click.ClickException(str(e))
        
        elif provider_name in ["together", "groq", "deepseek", "mistral", "perplexity"]:
            # Use OpenAI-compatible client factory
            model = provider_config.get("model")
            api_key = os.getenv(provider_config.get("api_key_env", f"{provider_name.upper()}_API_KEY"))
            base_url = provider_config.get("base_url")
            timeout = provider_config.get("timeout", 60)
            
            try:
                client = create_openai_compatible_client(
                    service=provider_name,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    timeout=timeout
                )
            except ImportError:
                raise click.ClickException(
                    "OpenAI package is not installed. "
                    "Install it with: pip install openai>=1.0.0"
                )
            except ValueError as e:
                raise click.ClickException(str(e))
        
        else:
            raise click.ClickException(
                f"Unknown provider: {provider_name}. "
                f"Supported providers: ollama, openai, anthropic, openrouter, together, groq, deepseek, mistral, perplexity"
            )
        
        # Check if client is available
        if not client.is_available():
            raise click.ClickException(
                f"AI client ({provider_name}) is not available. "
                f"Please check your configuration and ensure the service is running."
            )
        
        return client
        
    except FileNotFoundError:
        # Config file not found - use defaults
        click.echo("Warning: Configuration file not found. Using default settings.", err=True)
        # Default to Ollama
        client = OllamaClient()
        if not client.is_available():
            raise click.ClickException(
                "Ollama is not available. Please install and start Ollama, "
                "or configure another AI provider."
            )
        return client
    except Exception as e:
        raise click.ClickException(f"Failed to create AI client: {e}")


@click.group()
@click.version_option()
def main():
    """BDFEasyInput - Easy input generator for BDF quantum chemistry software."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output BDF input file")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file path")
def convert(input_file: str, output: Optional[str], config: Optional[str]):
    """Convert YAML input file to BDF input format."""
    try:
        # Load YAML
        with open(input_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # Validate
        validator = BDFValidator()
        try:
            _, warnings = validator.validate(yaml_data)
        except ValidationError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
        if warnings:
            click.echo("Validation warnings:", err=True)
            for warning in warnings:
                click.echo(f"  - {warning}", err=True)
        
        # Convert
        converter = BDFConverter()
        bdf_content = converter.convert(yaml_data)
        
        # Output
        if output:
            with open(output, 'w') as f:
                f.write(bdf_content)
            click.echo(f"BDF input file written to: {output}")
        else:
            click.echo(bdf_content)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def ai():
    """AI-powered task planning commands."""
    pass


@ai.command("plan")
@click.argument("query", required=False)
@click.option("-o", "--output", type=click.Path(), help="Output YAML file")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file path")
@click.option(
    "--provider",
    type=click.Choice(["ollama", "openai", "anthropic", "openrouter", "together", "groq", "deepseek", "mistral", "perplexity"]),
    help="AI provider to use (overrides config)"
)
@click.option("--model", help="Model name (overrides config)")
@click.option("--temperature", type=float, help="Sampling temperature (0.0-2.0)")
@click.option(
    "--no-validate",
    is_flag=True,
    help="Skip validation of generated YAML"
)
@click.option(
    "--stream/--no-stream",
    default=False,
    help="Stream AI output in real-time"
)
def ai_plan(
    query: Optional[str],
    output: Optional[str],
    config: Optional[str],
    provider: Optional[str],
    model: Optional[str],
    temperature: Optional[float],
    no_validate: bool,
    stream: bool
):
    """Generate YAML configuration from natural language query."""
    # Get query from argument or prompt
    if not query:
        query = click.prompt("Please describe your calculation task")
    
    try:
        # Get AI client
        if provider or model:
            # Override config with command-line options
            if provider == "ollama":
                client = OllamaClient(model_name=model or "llama3")
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise click.ClickException("OPENAI_API_KEY environment variable not set")
                client = OpenAIClient(model=model or "gpt-4", api_key=api_key)
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise click.ClickException("ANTHROPIC_API_KEY environment variable not set")
                client = AnthropicClient(model=model or "claude-3-sonnet-20240229", api_key=api_key)
            elif provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise click.ClickException("OPENROUTER_API_KEY environment variable not set")
                client = OpenRouterClient(model=model or "openai/gpt-4", api_key=api_key)
            elif provider in ["together", "groq", "deepseek", "mistral", "perplexity"]:
                client = create_openai_compatible_client(
                    service=provider,
                    model=model
                )
            else:
                client = get_ai_client_from_config(config)
        else:
            client = get_ai_client_from_config(config)
        
        # Create planner
        planner = TaskPlanner(
            ai_client=client,
            temperature=temperature or 0.7,
            validate_output=not no_validate
        )
        
        # Plan task
        click.echo("Planning task with AI...", err=True)
        if stream:
            response_text = ""
            for chunk in planner.plan_streaming(query):
                response_text += chunk
                click.echo(chunk, nl=False)
            click.echo("\n", nl=False)
            task_config = parse_ai_response(response_text)
        else:
            task_config = planner.plan(query)
        
        # Convert to YAML string
        yaml_content = yaml.dump(task_config, default_flow_style=False, allow_unicode=True)
        
        # Output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            click.echo(f"YAML configuration written to: {output}")
        else:
            click.echo("\nGenerated YAML configuration:")
            click.echo("=" * 50)
            click.echo(yaml_content)
        
    except PlanningError as e:
        click.echo(f"Planning failed: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@ai.command("chat")
@click.option("-o", "--output", type=click.Path(), help="Output YAML file")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file path")
@click.option(
    "--provider", 
    type=click.Choice(["ollama", "openai", "anthropic", "openrouter", "together", "groq", "deepseek", "mistral", "perplexity"])
)
@click.option("--model", help="Model name")
@click.option("--stream/--no-stream", default=True, help="Stream AI output in real-time")
def ai_chat(output: Optional[str], config: Optional[str], provider: Optional[str], model: Optional[str], stream: bool):
    """
    Interactive AI chat for task planning.
    
    This command starts an interactive conversation to help plan your calculation task.
    """
    click.echo("AI Task Planner - Interactive Mode")
    click.echo("Type 'exit' or 'quit' to end the conversation\n")
    
    try:
        # Get AI client
        if provider:
            if provider == "ollama":
                client = OllamaClient(model_name=model or "llama3")
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise click.ClickException("OPENAI_API_KEY environment variable not set")
                client = OpenAIClient(model=model or "gpt-4", api_key=api_key)
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise click.ClickException("ANTHROPIC_API_KEY environment variable not set")
                client = AnthropicClient(model=model or "claude-3-sonnet-20240229", api_key=api_key)
            elif provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise click.ClickException("OPENROUTER_API_KEY environment variable not set")
                client = OpenRouterClient(model=model or "openai/gpt-4", api_key=api_key)
            elif provider in ["together", "groq", "deepseek", "mistral", "perplexity"]:
                client = create_openai_compatible_client(
                    service=provider,
                    model=model
                )
        else:
            client = get_ai_client_from_config(config)
        
        planner = TaskPlanner(ai_client=client)
        
        conversation_history = []
        full_query = []
        
        while True:
            user_input = click.prompt("You", default="", show_default=False)
            
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            
            if not user_input.strip():
                continue
            
            full_query.append(user_input)
            conversation_history.append({"role": "user", "content": user_input})
            
            # Combine all conversation into a single query for now
            # (In a more sophisticated version, we could maintain conversation state)
            combined_query = "\n".join(full_query)
            
            try:
                click.echo("\nAI:", err=True)
                click.echo("Planning...", err=True)
                
                if stream:
                    response_text = ""
                    for chunk in planner.plan_streaming(combined_query):
                        response_text += chunk
                        click.echo(chunk, nl=False)
                    click.echo("\n", nl=False)
                    task_config = parse_ai_response(response_text)
                else:
                    task_config = planner.plan(combined_query)
                
                # Show YAML preview
                yaml_preview = yaml.dump(task_config, default_flow_style=False, allow_unicode=True)
                click.echo("\nGenerated configuration:")
                click.echo("=" * 50)
                click.echo(yaml_preview)
                
                # Ask if user wants to save or continue
                action = click.prompt(
                    "\n[s]ave, [c]ontinue, or [q]uit?",
                    default="c",
                    show_default=False
                )
                
                if action.lower() == "s":
                    # Validate before saving
                    validator = BDFValidator()
                    try:
                        _, warnings = validator.validate(task_config)
                        if warnings:
                            click.echo("Validation warnings:", err=True)
                            for w in warnings:
                                click.echo(f"  - {w}", err=True)
                    except ValidationError as e:
                        click.echo(str(e), err=True)
                        click.echo("Not saving due to validation errors. Please refine and try again.", err=True)
                        continue

                    if output:
                        output_path = output
                    else:
                        output_path = click.prompt("Output file", default="task.yaml")
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(yaml_preview)
                    
                    click.echo(f"Configuration saved to: {output_path}")
                    break
                elif action.lower() == "q":
                    break
                
            except PlanningError as e:
                click.echo(f"Planning failed: {e}", err=True)
                click.echo("Please try rephrasing your request.\n", err=True)
            except AIResponseParseError as e:
                click.echo(f"Parsing failed: {e}", err=True)
                click.echo("Try disabling streaming with --no-stream or refine your query.\n", err=True)
        
        click.echo("\nGoodbye!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output-dir", type=click.Path(), help="Output directory for results")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file path")
@click.option("--timeout", type=int, help="Timeout in seconds")
@click.option("--use-debug-dir", is_flag=True, help="Use bdfeasyinput/debug as working directory for testing")
def run(input_file: str, output_dir: Optional[str], config: Optional[str], timeout: Optional[int], use_debug_dir: bool):
    """Run BDF calculation from input file."""
    try:
        from .config import load_config, merge_config_with_defaults
        from .execution import create_runner
        
        # Load configuration
        yaml_config = load_config(config) if config else None
        if yaml_config:
            yaml_config = merge_config_with_defaults(yaml_config)
        
        # Create runner
        runner = create_runner(config=yaml_config)
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            # Use input file directory
            input_path = Path(input_file)
            output_path = input_path.parent
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Run calculation
        click.echo(f"Running BDF calculation from: {input_file}", err=True)
        click.echo(f"Output directory: {output_path}", err=True)
        
        # Pass use_debug_dir to runner if it's a BDFDirectRunner
        run_kwargs = {
            'timeout': timeout
        }
        # Check if runner supports use_debug_dir parameter
        import inspect
        run_signature = inspect.signature(runner.run)
        if 'use_debug_dir' in run_signature.parameters:
            run_kwargs['use_debug_dir'] = use_debug_dir
        
        result = runner.run(input_file, **run_kwargs)
        
        # Display results
        if result.get('status') == 'success':
            click.echo(f"✓ Calculation completed successfully", err=True)
            if result.get('output_file'):
                click.echo(f"Output file: {result['output_file']}", err=True)
            if result.get('error_file'):
                click.echo(f"Error file: {result.get('error_file')}", err=True)
        else:
            click.echo(f"✗ Calculation failed: {result.get('error', 'Unknown error')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("output_file", type=click.Path(exists=True))
@click.option("-i", "--input", type=click.Path(exists=True), help="BDF input file (optional)")
@click.option("-e", "--error", type=click.Path(exists=True), help="Error file (optional)")
@click.option("-o", "--output", type=click.Path(), help="Output report file")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file path")
@click.option("--format", type=click.Choice(["markdown", "html", "text"]), default="markdown", help="Report format")
@click.option("--task-type", help="Task type (e.g., energy, optimize, frequency)")
def analyze(
    output_file: str,
    input: Optional[str],
    error: Optional[str],
    output: Optional[str],
    config: Optional[str],
    format: str,
    task_type: Optional[str]
):
    """Analyze BDF calculation results using AI."""
    try:
        from .config import load_config, merge_config_with_defaults, get_ai_config
        from .analysis import QuantumChemistryAnalyzer, AnalysisReportGenerator
        from .analysis.parser import BDFOutputParser
        
        # Get AI client
        client = get_ai_client_from_config(config)
        
        # Get language setting from config
        analysis_config = config.get('analysis', {})
        ai_config = analysis_config.get('ai', {})
        language = ai_config.get('language', 'zh')  # Default to Chinese
        
        # Create analyzer
        analyzer = QuantumChemistryAnalyzer(ai_client=client)
        
        # Analyze
        click.echo("Analyzing results with AI...", err=True)
        analysis_result = analyzer.analyze(
            output_file=output_file,
            input_file=input,
            error_file=error,
            task_type=task_type,
            language=language
        )
        
        # Parse output for report
        parser = BDFOutputParser()
        parsed_data = parser.parse(output_file)
        
        # Generate report
        report_generator = AnalysisReportGenerator(format=format, language=language)
        report = report_generator.generate(
            analysis_result=analysis_result,
            parsed_data=parsed_data,
            output_file=output
        )
        
        if output:
            click.echo(f"Analysis report written to: {output}")
        else:
            click.echo("\n" + "=" * 50)
            click.echo(report)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.argument("output_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output JSON file")
@click.option("--task-type", help="Task type (auto-detect if not specified): single_point, optimize, frequency, optimize_frequency, excited")
def extract(output_file: str, output: Optional[str], task_type: Optional[str]):
    """Extract metrics from BDF output file."""
    try:
        from .extraction import BDFResultExtractor
        
        extractor = BDFResultExtractor()
        metrics = extractor.extract_metrics(output_file, task_type)
        
        result = metrics.to_dict()
        
        if output:
            import json
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"✓ Metrics written to: {output}", err=True)
        else:
            import json
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.group()
def yaml():
    """YAML generation and manipulation commands."""
    pass


@yaml.command("generate")
@click.argument("task_type", type=click.Choice(["energy", "optimize", "frequency", "tddft"]))
@click.option("-o", "--output", type=click.Path(), help="Output YAML file")
@click.option("--no-comments", is_flag=True, help="Don't include comments in template")
def yaml_generate(task_type: str, output: Optional[str], no_comments: bool):
    """Generate a YAML template for a given task type."""
    try:
        template = generate_yaml_template(
            task_type=task_type,
            output_path=output,
            include_comments=not no_comments
        )
        
        if output:
            click.echo(f"✓ YAML template generated: {output}")
        else:
            click.echo(yaml.dump(template, default_flow_style=False, allow_unicode=True))
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@yaml.command("from-xyz")
@click.argument("xyz_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output YAML file")
@click.option("-t", "--task-type", type=click.Choice(["energy", "optimize", "frequency", "tddft"]), 
              default="energy", help="Task type")
@click.option("--charge", type=int, default=0, help="Molecular charge")
@click.option("--multiplicity", type=int, default=1, help="Spin multiplicity")
@click.option("--functional", default="pbe0", help="DFT functional")
@click.option("--basis", default="cc-pvdz", help="Basis set")
@click.option("--no-validate", is_flag=True, help="Skip validation")
def yaml_from_xyz(
    xyz_file: str,
    output: Optional[str],
    task_type: str,
    charge: int,
    multiplicity: int,
    functional: str,
    basis: str,
    no_validate: bool
):
    """Generate YAML configuration from XYZ file."""
    try:
        method = {
            'type': 'dft',
            'functional': functional,
            'basis': basis
        }
        
        config = generate_yaml_from_xyz(
            xyz_path=xyz_file,
            task_type=task_type,
            charge=charge,
            multiplicity=multiplicity,
            method=method,
            output_path=output,
            validate=not no_validate
        )
        
        if output:
            click.echo(f"✓ YAML file generated: {output}")
        else:
            click.echo(yaml.dump(config, default_flow_style=False, allow_unicode=True))
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("batch-convert")
@click.argument("yaml_files", nargs=-1, type=click.Path(exists=True))
@click.option("-d", "--output-dir", type=click.Path(), help="Output directory")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
@click.option("--no-validate", is_flag=True, help="Skip validation")
def batch_convert(yaml_files: tuple, output_dir: Optional[str], overwrite: bool, no_validate: bool):
    """Convert multiple YAML files to BDF input files."""
    if not yaml_files:
        click.echo("Error: No YAML files specified", err=True)
        sys.exit(1)
    
    try:
        tool = ConversionTool(validate_input=not no_validate)
        results = tool.batch_convert(
            list(yaml_files),
            output_dir=output_dir,
            overwrite=overwrite,
            continue_on_error=True
        )
        
        success_count = sum(1 for v in results.values() if isinstance(v, Path))
        error_count = len(results) - success_count
        
        click.echo(f"\nConversion complete:")
        click.echo(f"  ✓ Success: {success_count}")
        if error_count > 0:
            click.echo(f"  ✗ Errors: {error_count}")
            for path, result in results.items():
                if isinstance(result, Exception):
                    click.echo(f"    - {path}: {result}", err=True)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("preview")
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--max-lines", type=int, default=50, help="Maximum lines to show")
def preview(yaml_file: str, max_lines: int):
    """Preview BDF input without saving to file."""
    try:
        tool = ConversionTool(validate_input=True)
        preview_content, config = tool.preview(yaml_file, max_lines=max_lines)
        
        click.echo("YAML Configuration:")
        click.echo(yaml.dump(config, default_flow_style=False, allow_unicode=True))
        click.echo("\n" + "="*70)
        click.echo("BDF Input Preview:")
        click.echo(preview_content)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("validate-yaml")
@click.argument("yaml_file", type=click.Path(exists=True))
def validate_yaml(yaml_file: str):
    """Validate YAML configuration file."""
    try:
        tool = ConversionTool(validate_input=True)
        is_valid, errors, warnings = tool.validate_yaml(yaml_file)
        
        if is_valid:
            click.echo(f"✓ YAML file is valid: {yaml_file}")
            if warnings:
                click.echo("\nWarnings:")
                for warning in warnings:
                    click.echo(f"  - {warning}")
        else:
            click.echo(f"✗ YAML file is invalid: {yaml_file}", err=True)
            if errors:
                click.echo("\nErrors:")
                for error in errors:
                    click.echo(f"  - {error}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("query", required=False)
@click.option("-o", "--output-dir", type=click.Path(), default="./results", help="Output directory")
@click.option("-c", "--config", type=click.Path(exists=True), help="Configuration file path")
@click.option("--run/--no-run", default=False, help="Run calculation after generating input")
@click.option("--analyze/--no-analyze", default=False, help="Analyze results after calculation")
@click.option("--provider", type=click.Choice(["ollama", "openai", "anthropic"]), help="AI provider")
@click.option("--model", help="AI model name")
def workflow(
    query: Optional[str],
    output_dir: str,
    config: Optional[str],
    run: bool,
    analyze: bool,
    provider: Optional[str],
    model: Optional[str]
):
    """Complete workflow: plan → convert → run → analyze."""
    try:
        from pathlib import Path
        from .config import load_config, merge_config_with_defaults
        from .converter import BDFConverter
        from .execution import create_runner
        from .analysis import QuantumChemistryAnalyzer, AnalysisReportGenerator
        from .analysis.parser import BDFOutputParser
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Plan task
        if not query:
            query = click.prompt("Please describe your calculation task")
        
        click.echo("Step 1: Planning task with AI...", err=True)
        client = get_ai_client_from_config(config)
        if provider or model:
            if provider == "ollama":
                client = OllamaClient(model_name=model or "llama3")
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise click.ClickException("OPENAI_API_KEY environment variable not set")
                client = OpenAIClient(model=model or "gpt-4", api_key=api_key)
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise click.ClickException("ANTHROPIC_API_KEY environment variable not set")
                client = AnthropicClient(model=model or "claude-3-sonnet-20240229", api_key=api_key)
            elif provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    raise click.ClickException("OPENROUTER_API_KEY environment variable not set")
                client = OpenRouterClient(model=model or "openai/gpt-4", api_key=api_key)
            elif provider in ["together", "groq", "deepseek", "mistral", "perplexity"]:
                client = create_openai_compatible_client(
                    service=provider,
                    model=model
                )
        
        from .ai import TaskPlanner
        planner = TaskPlanner(ai_client=client)
        task_config = planner.plan(query)
        
        # Save YAML
        yaml_file = output_path / "task.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(task_config, f, default_flow_style=False, allow_unicode=True)
        click.echo(f"✓ Task configuration saved to: {yaml_file}", err=True)
        
        # Step 2: Convert to BDF
        click.echo("Step 2: Converting to BDF input...", err=True)
        converter = BDFConverter()
        bdf_content = converter.convert(task_config)
        
        bdf_input_file = output_path / "bdf_input.inp"
        with open(bdf_input_file, 'w') as f:
            f.write(bdf_content)
        click.echo(f"✓ BDF input file written to: {bdf_input_file}", err=True)
        
        # Step 3: Run calculation (if requested)
        execution_result = None
        if run:
            click.echo("Step 3: Running BDF calculation...", err=True)
            yaml_config = load_config(config) if config else None
            if yaml_config:
                yaml_config = merge_config_with_defaults(yaml_config)
            
            runner = create_runner(config=yaml_config)
            execution_result = runner.run(
                str(bdf_input_file),
                output_dir=str(output_path)
            )
            
            if execution_result.get('status') == 'success':
                click.echo(f"✓ Calculation completed successfully", err=True)
            else:
                click.echo(f"✗ Calculation failed: {execution_result.get('error', 'Unknown error')}", err=True)
                if not analyze:  # If analyze is not requested, exit
                    sys.exit(1)
        
        # Step 4: Analyze results (if requested and calculation succeeded)
        if analyze and execution_result and execution_result.get('status') == 'success':
            click.echo("Step 4: Analyzing results with AI...", err=True)
            
            output_file = execution_result.get('output_file')
            if not output_file:
                click.echo("Warning: No output file found, skipping analysis", err=True)
            else:
                analyzer = QuantumChemistryAnalyzer(ai_client=client)
                analysis_result = analyzer.analyze(
                    output_file=output_file,
                    input_file=str(bdf_input_file),
                    error_file=execution_result.get('error_file'),
                    task_type=task_config.get('task', {}).get('type')
                )
                
                parser = BDFOutputParser()
                parsed_data = parser.parse(output_file)
                
                report_generator = AnalysisReportGenerator(format="markdown")
                report_file = output_path / "analysis_report.md"
                report = report_generator.generate(
                    analysis_result=analysis_result,
                    parsed_data=parsed_data,
                    output_file=str(report_file)
                )
                
                click.echo(f"✓ Analysis report written to: {report_file}", err=True)
        elif analyze and not run:
            click.echo("Warning: --analyze requires --run. Skipping analysis.", err=True)
        
        click.echo("\n✓ Workflow completed successfully!", err=True)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
