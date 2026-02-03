import asyncio
import click
from pathlib import Path
from rich.console import Console
from shipsight.config import load_config, get_global_config_path
from shipsight.engine.orchestrator import Orchestrator
from shipsight.engine.discovery import ConfigDiscovery
from shipsight.capture.capture import CaptureEngine
from shipsight.capture.crawler import Crawler
from shipsight.ai.intelligence import IntelligenceEngine
from shipsight.ai.narrative import NarrativeGenerator
from shipsight.artifacts import ArtifactManager
from shipsight.capture.carbon import Carbonizer
import yaml

console = Console()

@click.group()
def main():
    """ShipSight: Convert your running project into shareable proof."""
    pass

@main.command()
@click.option('--openai', help='Set OpenAI API Key')
@click.option('--anthropic', help='Set Anthropic API Key')
@click.option('--groq', help='Set Groq API Key')
def auth(openai, anthropic, groq):
    """Save API keys globally for persistent use."""
    path = get_global_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    config = {}
    if path.exists():
        with open(path, "r") as f:
            config = yaml.safe_load(f) or {}
    
    if "ai" not in config: config["ai"] = {}
    
    if openai: 
        config["ai"]["openai_api_key"] = openai
        config["ai"]["provider"] = "openai"
        config["ai"]["model"] = "gpt-4o-mini"
    if anthropic: 
        config["ai"]["anthropic_api_key"] = anthropic
        config["ai"]["provider"] = "anthropic"
        config["ai"]["model"] = "claude-3-5-sonnet-20240620"
    if groq: 
        config["ai"]["groq_api_key"] = groq
        config["ai"]["provider"] = "groq"
        config["ai"]["model"] = "llama-3.1-8b-instant"
    
    with open(path, "w") as f:
        yaml.dump(config, f)
    
    console.print(f"[green]API keys saved to {path}[/green]")

@main.command()
@click.argument('path', default='.')
@click.option('--config', '-c', default='shipsight.yml', help='Path to config file.')
@click.option('--static', is_flag=True, help='Skip execution and only generate code snaps/narratives.')
def run(path, config, static):
    """Run ShipSight on a project."""
    project_path = Path(path)
    config_file = project_path / config
    
    if not config_file.exists():
        console.print(f"[yellow]No {config} found at {project_path}. Running auto-init...[/yellow]")
        discovery = ConfigDiscovery(project_path)
        suggestion = discovery.infer_config()
        discovery.write_suggestion(suggestion, config_file)
        console.print(f"[green]Created default {config}. Continuing run...[/green]")

    asyncio.run(_run_flow(project_path, Path(config), static))

async def _run_flow(project_path: Path, config_path: Path, static: bool = False):
    console.print(f"[bold blue]ShipSight: Analyzing project at {project_path}[/bold blue]")
    
    # 1. Load Config
    cfg = load_config(project_path / config_path)
    if static:
        cfg.run.strategy = "static"
    
    output_dir = project_path / cfg.output.path
    artifact_manager = ArtifactManager(output_dir)
    
    # 2. Intelligence Layer
    intel = IntelligenceEngine(project_path)
    analysis = intel.analyze_stack()
    heroes = intel.get_hero_code()
    artifact_manager.save_json("metadata.json", {**analysis, "heroes": list(heroes.keys())})
    context = intel.get_summary_context(analysis, heroes)

    # 3. Execution Engine
    orchestrator = Orchestrator(project_path, cfg)
    if orchestrator.start():
        try:
            # 4. Use dynamically detected URL (fixes IPv6/localhost issues)
            base_url = orchestrator.detected_url or f"http://localhost:{orchestrator.detected_port or cfg.run.port or 3000}"
            
            if not orchestrator.is_script and not orchestrator.is_static:
                console.print(f"[blue]Using base URL: {base_url}[/blue]")
                
                # Auto-discovery if routes are default
                if cfg.capture.routes == ["/"]:
                    crawler = Crawler(base_url)
                    cfg.capture.routes = await crawler.discover_routes()
                    console.print(f"[blue]Discovered routes: {cfg.capture.routes}[/blue]")

                capture = CaptureEngine(cfg, output_dir)
                await capture.capture_screenshots(base_url)
            else:
                mode_name = "Static" if orchestrator.is_static else "Script"
                console.print(f"[yellow]{mode_name} Mode detected. Skipping web capture steps.[/yellow]")
            
            # 5. Narrative Generation
            narrative = NarrativeGenerator(cfg.ai)
            dna = analysis.get("dna", "GENERAL_SOFTWARE")
            readme = await narrative.generate_readme(context, dna=dna, heroes=heroes)
            linkedin = await narrative.generate_linkedin_post(context, dna=dna)
            
            # 6. Code Carbonization (Visual Proof)
            carbon = Carbonizer(output_dir)
            for file, code in heroes.items():
                await carbon.carbonize(code, f"{file}.png")
            
            artifact_manager.save_markdown("README.generated.md", readme)
            artifact_manager.save_markdown("linkedin.post.md", linkedin)
            
            console.print("[bold green]ShipSight process complete![/bold green]")
            console.print(f"Artifacts available in {output_dir}")

        finally:
            orchestrator.stop()
    else:
        console.print("[bold red]Execution Engine failed to start project.[/bold red]")
        
        # Diagnostics
        last_log = orchestrator.get_last_log(15)
        if last_log:
            console.print("[dim]Last 15 lines of project_startup.log:[/dim]")
            console.print(f"[red]{last_log}[/red]")
        
        # Fallback Prompt
        if not static:
            if click.confirm("[yellow]Would you like to try running in Static Mode (analysis only)? [/yellow]", default=True):
                await _run_flow(project_path, config_path, static=True)

if __name__ == "__main__":
    main()
