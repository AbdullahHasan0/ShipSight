from pathlib import Path
from rich.console import Console

console = Console()

class ArtifactManager:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_markdown(self, filename: str, content: str):
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]Saved artifact to {filepath}[/green]")

    def save_json(self, filename: str, data: dict):
        import json
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        console.print(f"[green]Saved metadata to {filepath}[/green]")
