import os
import yaml
from pathlib import Path
from typing import Optional, Dict

class ConfigDiscovery:
    def __init__(self, project_path: Path):
        self.project_path = project_path

    def infer_config(self) -> Dict:
        """Analyze project files and return a suggested config dict."""
        suggestion = {
            "run": {
                "strategy": "local",
                "port": 3000,
                "command": ""
            },
            "capture": {
                "routes": ["/"]
            },
            "output": {
                "path": "shipsight_output"
            }
        }

        # 1. Detect Docker
        if (self.project_path / "docker-compose.yml").exists():
            suggestion["run"]["strategy"] = "docker"
            suggestion["run"]["command"] = "docker-compose up"
            # Don't return yet, detect what's INSIDE the docker for local fallback

        # 2. Detect Node.js / Web
        if (self.project_path / "package.json").exists():
            with open(self.project_path / "package.json", "r") as f:
                content = f.read()
                if '"next"' in content:
                    suggestion["run"]["command"] = suggestion["run"]["command"] or "npm run dev"
                    suggestion["run"]["port"] = 3000
                elif '"vite"' in content:
                    suggestion["run"]["command"] = suggestion["run"]["command"] or "npm run dev"
                    suggestion["run"]["port"] = 5173
                else:
                    suggestion["run"]["command"] = suggestion["run"]["command"] or "npm start"
                    suggestion["run"]["port"] = 3000

        # 3. Detect Python
        elif (self.project_path / "requirements.txt").exists() or (self.project_path / "pyproject.toml").exists():
            req_content = ""
            for req_file in ["requirements.txt", "pyproject.toml"]:
                p = self.project_path / req_file
                if p.exists():
                    req_content += p.read_text(errors="ignore").lower()
            
            if "fastapi" in req_content:
                if (self.project_path / "app" / "main.py").exists():
                    suggestion["run"]["command"] = "uvicorn app.main:app --port 8000"
                elif (self.project_path / "main.py").exists():
                    suggestion["run"]["command"] = "uvicorn main:app --port 8000"
                else:
                    suggestion["run"]["command"] = "uvicorn main:app --port 8000"
                suggestion["run"]["port"] = 8000
            elif "flask" in req_content:
                if (self.project_path / "main.py").exists():
                    suggestion["run"]["command"] = "python main.py"
                elif (self.project_path / "app.py").exists():
                    suggestion["run"]["command"] = "python app.py"
                else:
                    suggestion["run"]["command"] = "flask run"
                suggestion["run"]["port"] = 5000 # Default Flask port
            elif "django" in req_content:
                suggestion["run"]["command"] = "python manage.py runserver"
                suggestion["run"]["port"] = 8000
            else:
                # Check if this is a CLI tool or library (not a runnable script)
                is_cli_or_lib = False
                
                # Check pyproject.toml for console_scripts
                pyproject_path = self.project_path / "pyproject.toml"
                if pyproject_path.exists():
                    try:
                        pyproject_content = pyproject_path.read_text(errors="ignore")
                        if "console_scripts" in pyproject_content or "[project.scripts]" in pyproject_content:
                            is_cli_or_lib = True
                    except: pass
                
                # Check setup.py for console_scripts
                setup_path = self.project_path / "setup.py"
                if setup_path.exists():
                    try:
                        setup_content = setup_path.read_text(errors="ignore")
                        if "console_scripts" in setup_content or "entry_points" in setup_content:
                            is_cli_or_lib = True
                    except: pass
                
                if is_cli_or_lib:
                    # This is a CLI tool or library, not a runnable web service
                    suggestion["run"]["command"] = ""
                    suggestion["run"]["port"] = 0
                elif (self.project_path / "main.py").exists():
                    suggestion["run"]["command"] = "python main.py"
                    suggestion["run"]["port"] = 0
                elif (self.project_path / "app.py").exists():
                    suggestion["run"]["command"] = "python app.py"
                    suggestion["run"]["port"] = 0
                else:
                    # Unknown Python project structure
                    suggestion["run"]["command"] = ""
                    suggestion["run"]["port"] = 0

        # 4. Detect Flutter
        elif (self.project_path / "pubspec.yaml").exists():
            suggestion["run"]["strategy"] = "local"
            # Defaulting to web-server for capture ease, user can change to -d chrome
            suggestion["run"]["command"] = "flutter run -d web-server --web-port 8080"
            suggestion["run"]["port"] = 8080

        return suggestion

    def write_suggestion(self, suggestion: Dict, path: Path):
        """Save the suggested config to shipsight.yml."""
        with open(path, "w") as f:
            yaml.dump(suggestion, f, sort_keys=False)
