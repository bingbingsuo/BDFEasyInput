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
from .ai.client import OllamaClient, OpenAIClient, AnthropicClient, AIClient


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
        else:
            raise click.ClickException(f"Unknown provider: {provider_name}")
        
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
    type=click.Choice(["ollama", "openai", "anthropic"]),
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
@click.option("--provider", type=click.Choice(["ollama", "openai", "anthropic"]))
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


if __name__ == "__main__":
    main()
