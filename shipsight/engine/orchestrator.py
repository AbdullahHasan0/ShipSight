import subprocess
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from shipsight.config import ShipSightConfig
from shipsight.engine.readiness import wait_for_ready, is_port_open, auto_wait_for_ready
import click

console = Console()

class Orchestrator:
    def __init__(self, project_path: Path, config: ShipSightConfig):
        self.project_path = project_path
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.detected_port: Optional[int] = config.run.port
        self.detected_url: Optional[str] = None
        self.log_file = None
        self.is_script = False
        self.is_static = False

    def detect_stack(self):
        """Simple stack detection based on files. Returns the local tech stack even if Docker is present."""
        if (self.project_path / "package.json").exists():
            return "node"
        if (self.project_path / "requirements.txt").exists() or (self.project_path / "pyproject.toml").exists():
            return "python"
        if (self.project_path / "pubspec.yaml").exists():
            return "flutter"
        if (self.project_path / "docker-compose.yml").exists():
            return "docker"
        return "unknown"

    def start(self) -> bool:
        stack = self.detect_stack()
        console.print(f"[blue]Detected stack: {stack}[/blue]")

        if self.config.run.strategy == "static":
            console.print("[yellow]Static Mode: Skipping project execution (No-Op).[/yellow]")
            self.is_static = True
            return True
        elif self.config.run.strategy == "docker" or stack == "docker":
            return self._start_docker()
        else:
            return self._start_local(stack)

    def _start_local(self, stack: str) -> bool:
        cmd = self.config.run.command
        
        # If the command is a Docker command but we are in _start_local, 
        # it means we are falling back. We must ignore the Docker command.
        is_docker_cmd = cmd and ("docker" in cmd.lower())
        
        if not cmd or is_docker_cmd:
            if stack == "node":
                cmd = "npm run dev"
            elif stack == "python":
                cmd = "python main.py" # Placeholder
            elif is_docker_cmd:
                console.print(f"[red]Cannot run '{cmd}' locally. Skipping...[/red]")
                return False
            else:
                console.print("[red]No run command specified or detected.[/red]")
                return False

        # 1. Check for port conflict
        if self.config.run.port and is_port_open("localhost", self.config.run.port):
            console.print(f"[bold yellow]Warning: Port {self.config.run.port} is already in use.[/bold yellow]")
            choice = click.prompt(
                "Should ShipSight [u]use the existing service, [k]ill the process using it, or [c]ancel?",
                type=click.Choice(['u', 'k', 'c'], case_sensitive=False),
                default='u'
            )
            
            if choice == 'u':
                # No need to wait, already up
                self.detected_port = self.config.run.port
                return True
            elif choice == 'k':
                self.kill_port(self.config.run.port)
            else:
                return False

        # 2. Start process
        console.print(f"[yellow]Starting local process: {cmd}[/yellow]")
        
        # 3. Handle Virtual Environments (Python)
        env = os.environ.copy()
        venv_dirs = [".venv", "venv"]
        for venv_name in venv_dirs:
            venv_path = self.project_path / venv_name
            if venv_path.exists():
                console.print(f"[blue]Detected local virtual environment: {venv_name}[/blue]")
                if os.name == "nt":
                    scripts_path = venv_path / "Scripts"
                    env["PATH"] = f"{scripts_path}{os.pathsep}{env.get('PATH', '')}"
                else:
                    bin_path = venv_path / "bin"
                    env["PATH"] = f"{bin_path}{os.pathsep}{env.get('PATH', '')}"
                env["VIRTUAL_ENV"] = str(venv_path)
                break

        # Create output dir if needed and log startup
        output_dir = self.project_path / self.config.output.path
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "project_startup.log"
        
        self.log_file = open(log_path, "w", encoding="utf-8")
        
        self.process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=self.project_path,
            stdout=self.log_file,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        )
        
        # Wait for readiness dynamically
        res_port, res_url = auto_wait_for_ready("localhost", self.config.run.port, self.process)
        if res_port:
            if res_port == -1:
                self.is_script = True
                return True
            self.detected_port = res_port
            self.detected_url = res_url
            return True
        return False

    def is_docker_running(self) -> bool:
        """Check if Docker daemon is responsive."""
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
            return True
        except:
            return False

    def _start_docker(self) -> bool:
        stack = self.detect_stack()
        
        if not self.is_docker_running():
            console.print("[yellow]Docker daemon is not running.[/yellow]")
            if stack != "unknown" and stack != "docker":
                if click.confirm(f"Should ShipSight try running the {stack} stack locally instead?"):
                    return self._start_local(stack)
            return False

        console.print("[yellow]Starting Docker Compose...[/yellow]")
        try:
            # Note: capturing output to avoid messy logs, but it might hide 'up' progress
            subprocess.run(["docker-compose", "up", "-d"], cwd=self.project_path, check=True, capture_output=True)
            
            # For Docker, process detection is harder (it's in a container)
            # We'll just wait for the configured port or common defaults
            if self.config.run.port:
                if wait_for_ready("localhost", self.config.run.port):
                    self.detected_port = self.config.run.port
                    # Construct default local URL for Docker
                    self.detected_url = f"http://localhost:{self.detected_port}"
                    return True
            return False
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_details = ""
            if isinstance(e, subprocess.CalledProcessError):
                error_details = e.stderr.decode() if e.stderr else str(e)
            else:
                error_details = "Docker-Compose not found on system."

            console.print(f"[red]Docker Compose failed: {error_details}[/red]")
            
            if stack != "unknown" and stack != "docker":
                if click.confirm(f"Should ShipSight try running the {stack} stack locally instead?"):
                    return self._start_local(stack)
            return False

    def kill_port(self, port: int):
        """Forcefully kill whatever is running on a specific port (Windows only for now)."""
        if os.name == "nt":
            console.print(f"[yellow]Searching for process on port {port}...[/yellow]")
            try:
                # Find PID using netstat
                result = subprocess.run(
                    f"netstat -ano | findstr :{port}", 
                    shell=True, capture_output=True, text=True
                )
                lines = result.stdout.strip().split("\n")
                pids = set()
                for line in lines:
                    parts = line.split()
                    if len(parts) > 4 and "LISTENING" in line:
                        pids.add(parts[-1])
                
                for pid in pids:
                    console.print(f"[red]Killing process {pid} on port {port}...[/red]")
                    subprocess.run(["taskkill", "/F", "/T", "/PID", pid], capture_output=True)
            except Exception as e:
                console.print(f"[red]Failed to kill port {port}: {e}[/red]")
        else:
            # Linux/Mac equivalent
            subprocess.run(f"fuser -k {port}/tcp", shell=True, capture_output=True)

    def stop(self):
        if self.process:
            if os.name == "nt":
                # Kill process tree on Windows
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)], capture_output=True)
            else:
                self.process.terminate()
            console.print("[blue]Local process stopped.[/blue]")
        
        if self.log_file:
            self.log_file.close()
            self.log_file = None

        if (self.project_path / "docker-compose.yml").exists():
            subprocess.run(["docker-compose", "down"], cwd=self.project_path, capture_output=True)
            console.print("[blue]Docker services stopped.[/blue]")

    def get_last_log(self, lines: int = 10) -> str:
        """Read the last N lines of the startup log."""
        log_path = self.project_path / self.config.output.path / "project_startup.log"
        if not log_path.exists():
            return ""
        
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except:
            return ""
