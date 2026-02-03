import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv() # Load from .env if it exists

class RunConfig(BaseModel):
    strategy: str = "local" # local, docker, or static
    port: Optional[int] = None
    command: Optional[str] = None

class CaptureConfig(BaseModel):
    routes: List[str] = Field(default_factory=lambda: ["/"])
    auth_enabled: bool = False
    viewport: dict = {"width": 1280, "height": 720}

class OutputConfig(BaseModel):
    anonymize: bool = False
    formats: List[str] = ["readme", "linkedin"]
    path: str = "shipsight_output"

class AIConfig(BaseModel):
    provider: str = "ollama" # ollama, openai, anthropic, or groq
    model: str = "llama-3.1-8b-instant"
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

class ShipSightConfig(BaseModel):
    run: RunConfig = Field(default_factory=RunConfig)
    capture: CaptureConfig = Field(default_factory=CaptureConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    ai: AIConfig = Field(default_factory=AIConfig)

def get_global_config_path() -> Path:
    return Path.home() / ".shipsight" / "config.yml"

def load_config(local_path: Path) -> ShipSightConfig:
    global_path = get_global_config_path()
    
    # 1. Load global config (keys)
    config_data = {}
    if global_path.exists():
        with open(global_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
    
    # 2. Load local project config (runs/routes) override global
    if local_path.exists():
        with open(local_path, "r") as f:
            local_data = yaml.safe_load(f) or {}
            # Deep merge simple dicts
            for key in ["run", "capture", "output", "ai"]:
                if key in local_data:
                    if key not in config_data:
                        config_data[key] = {}
                    config_data[key].update(local_data[key])
    
    # 3. AUTO-MIGRATION: Swap decommissioned Groq models
    ai_settings = config_data.get("ai", {})
    current_model = ai_settings.get("model")
    
    # List of known decommissioned Groq models
    decommissioned = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
    
    if ai_settings.get("provider") == "groq":
        if current_model in decommissioned or not current_model:
            config_data["ai"]["model"] = "llama-3.1-8b-instant"

    # 4. ENV VAR OVERRIDES (Highest Priority)
    
    # helper to check nested keys
    if "ai" not in config_data:
        config_data["ai"] = {}
        
    import os
    
    # Map Env Vars to Config
    env_map = {
        "OPENAI_API_KEY": ("ai", "openai_api_key"),
        "ANTHROPIC_API_KEY": ("ai", "anthropic_api_key"),
        "GROQ_API_KEY": ("ai", "groq_api_key"),
        "AI_PROVIDER": ("ai", "provider"),
        "AI_MODEL": ("ai", "model"),
    }
    
    for env_key, (section, config_key) in env_map.items():
        val = os.getenv(env_key)
        if val:
            config_data[section][config_key] = val

    # 5. Smart Provider Detection (if still default)
    # If provider is explicitly set by user (via yaml or env), respect it.
    # If it's effectively default (ollama) but we see keys for others, switch.
    
    ai_config = config_data.get("ai", {})
    provider = ai_config.get("provider", "ollama")
    
    # If user hasn't explicitly set provider to something else, or if it's default
    if provider == "ollama":
        if ai_config.get("openai_api_key"):
            config_data["ai"]["provider"] = "openai"
            if not ai_config.get("model"): config_data["ai"]["model"] = "gpt-4-turbo-preview"
        elif ai_config.get("anthropic_api_key"):
            config_data["ai"]["provider"] = "anthropic"
            if not ai_config.get("model"): config_data["ai"]["model"] = "claude-3-opus-20240229"
        elif ai_config.get("groq_api_key"):
            config_data["ai"]["provider"] = "groq"
            if not ai_config.get("model"): config_data["ai"]["model"] = "llama-3.1-8b-instant"

    return ShipSightConfig(**config_data)
