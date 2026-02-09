import pytest
from pathlib import Path
import yaml
from shipsight.engine.discovery import ConfigDiscovery

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    def _create(files: dict):
        for name, content in files.items():
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return tmp_path
    return _create

def test_detect_nodejs_nextjs(temp_project):
    project = temp_project({
        "package.json": '{"dependencies": {"next": "14.0.0"}}'
    })
    discovery = ConfigDiscovery(project)
    config = discovery.infer_config()
    
    assert config["run"]["command"] == "npm run dev"
    assert config["run"]["port"] == 3000

def test_detect_python_fastapi(temp_project):
    project = temp_project({
        "requirements.txt": "fastapi\nuvicorn",
        "app/main.py": "app = FastAPI()"
    })
    discovery = ConfigDiscovery(project)
    config = discovery.infer_config()
    
    assert "uvicorn" in config["run"]["command"]
    assert config["run"]["port"] == 8000

def test_detect_docker(temp_project):
    project = temp_project({
        "docker-compose.yml": "services:\n  app:\n    image: node"
    })
    discovery = ConfigDiscovery(project)
    config = discovery.infer_config()
    
    assert config["run"]["strategy"] == "docker"
    assert config["run"]["command"] == "docker-compose up"

def test_detect_flutter(temp_project):
    project = temp_project({
        "pubspec.yaml": "name: my_app"
    })
    discovery = ConfigDiscovery(project)
    config = discovery.infer_config()
    
    assert "flutter run" in config["run"]["command"]
    assert config["run"]["port"] == 8080
