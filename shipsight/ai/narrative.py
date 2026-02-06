import httpx
from typing import Optional
from rich.console import Console

from shipsight.config import AIConfig

console = Console()

class NarrativeGenerator:
    def __init__(self, config: AIConfig, project_name: str = "Unknown"):
        self.config = config
        self.project_name = project_name

    def _log_usage(self, provider: str, model: str, usage: dict):
        """Log token usage to ~/.shipsight/token_usage.jsonl"""
        try:
            import json
            import datetime
            from pathlib import Path
            
            log_dir = Path.home() / ".shipsight"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "token_usage.jsonl"
            
            record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "project": self.project_name,
                "provider": provider,
                "model": model,
                "usage": usage
            }
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            # logging shouldn't crash the app
            console.print(f"[dim yellow]Warning: Failed to log token usage: {e}[/dim yellow]")

    async def generate_readme(self, context: str, dna: str = "GENERAL_SOFTWARE", heroes: dict = None) -> str:
        
        # DNA-based Persona Selection
        persona = "Product Manager / Lead Engineer"
        focus = "FEATURES and USER VALUE"
        if dna == "MOBILE":
            persona = "Senior Mobile Engineer / App Launcher"
            focus = "UX, TOUCH INTERACTIONS, and APP STORE APPEAL"
        elif dna == "CLI":
            persona = "Open Source Maintainer / DevTool Expert"
            focus = "DEVELOPER PRODUCTIVITY, AUTOMATION, and EASE OF USE"
        
        prompt = f"""
        Act as a {persona}. Generate a professional README.md focused on {focus}.
        
        {context}
        
        ### STRICT CONTEXT PURITY RULES:
        - ONLY use information provided in the CONTEXT above.
        - DO NOT HALLUCINATE features like "Website Roasting" or "SEO Analysis" unless explicitly in context.
        - If project is {dna} (e.g. Flutter/Mobile), use appropriate terminology (Screen vs Page, Tap vs Click).
        - Focus on "What the project does", "Key Features", and "How to use it".
        - DO NOT use emojis anywhere in the README.
        """
        return await self._call_llm(prompt)

    async def generate_linkedin_post(self, context: str, dna: str = "GENERAL_SOFTWARE") -> str:
        
        # DNA-based Guidelines
        guidelines = "- Hook: A clear, problem-solving opening."
        if dna == "MOBILE":
            guidelines = "- Hook: Focus on the 'App Utility' or 'User Experience'.\n- Use mobile terms: 'Tap', 'Native feel', 'On the go'."
        elif dna == "CLI":
            guidelines = "- Hook: Focus on 'Efficiency' and 'Developer Experience'.\n- Use dev terms: 'Script', 'Workflow', 'Automation'."
            
        prompt = f"""
        Generate an "Authentic Developer LinkedIn Post" as the CREATOR of this project.
        
        CONTEXT:
        {context}
        
        TASK:
        1. Start with the PROBLEM: "I needed a way to..." or "I wanted to build..."
        2. Explain the SOLUTION: "So I built {self.project_name}, a [What it is]..."
        3. List 3 Technical Features: "It features X, Y, and Z..."
        
        GUIDELINES:
        {guidelines}
        - Voice: First-person ("I built", "I used").
        
        TASK:
        1. Start with the PROBLEM: "I needed a way to..." or "I wanted to build..."
        2. Explain the SOLUTION: "So I built {self.project_name}, a [What it is]..."
        3. List 3 Technical Features: "It features X, Y, and Z..."
        
        GUIDELINES:
        {guidelines}
        - Voice: First-person ("I built", "I used").
        - Focus: 80% on the CODE/FEATURES, 20% on the backend stack.
        - NO EMOJIS (except maybe one at the end).
        
        ### ANTI-DIARY RULE:
        - DO NOT talk about "learning about yourself", "personal growth", "versatility", or "challenges". 
        - DO NOT say "This project showcases my ability to..."
        - Keep it technical and product-focused.
        
        ### ANTI-HYPE GUARDRAILS:
        - DO NOT use: "Revolutionary", "Groundbreaking", "Game-changer", "Cosmic".
        - Simple tone: "Here is what I made. Here is how it works."
        """
        return await self._call_llm(prompt)

    async def _call_llm(self, prompt: str) -> str:
        if self.config.provider == "ollama":
            # Call Ollama local API
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:11434/api/generate",
                        json={"model": self.config.model, "prompt": prompt, "stream": False},
                        timeout=30.0
                    )
                    result_json = response.json()
                    
                    # Log Usage (Ollama)
                    # Ollama returns 'prompt_eval_count' and 'eval_count'
                    if "prompt_eval_count" in result_json:
                         self._log_usage("ollama", self.config.model, {
                             "prompt_tokens": result_json.get("prompt_eval_count", 0),
                             "completion_tokens": result_json.get("eval_count", 0),
                             "total_tokens": result_json.get("prompt_eval_count", 0) + result_json.get("eval_count", 0)
                         })

                    return result_json.get("response", "Error: LLM failed to respond.")
            except Exception as e:
                return f"Error connecting to local LLM: {e}. Ensure Ollama is running or configure OpenAI/Anthropic."
        elif self.config.provider == "openai":
            api_key = self.config.openai_api_key
            if not api_key:
                return "Error: OpenAI provider selected but no API key provided (set OPENAI_API_KEY)."
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.config.model,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=60.0
                    )
                    result = response.json()
                    
                    if response.status_code != 200:
                        error_msg = result.get("error", {}).get("message", "Unknown error")
                        return f"Error from OpenAI API ({response.status_code}): {error_msg}"
                    
                    # Log Usage (OpenAI)
                    if "usage" in result:
                        self._log_usage("openai", self.config.model, result["usage"])
                        
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error calling OpenAI: {e}"
        elif self.config.provider == "anthropic":
            api_key = self.config.anthropic_api_key
            if not api_key:
                return "Error: Anthropic provider selected but no API key provided (set ANTHROPIC_API_KEY)."
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": api_key,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.config.model,
                            "max_tokens": 4096,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=60.0
                    )
                    result = response.json()
                    
                    if response.status_code != 200:
                        error_type = result.get("error", {}).get("type", "Unknown type")
                        error_msg = result.get("error", {}).get("message", "Unknown error")
                        return f"Error from Anthropic API ({response.status_code}): {error_type} - {error_msg}"
                    
                    # Log Usage (Anthropic)
                    if "usage" in result:
                        usage = result["usage"]
                        # standardize fields
                        std_usage = {
                            "prompt_tokens": usage.get("input_tokens", 0),
                            "completion_tokens": usage.get("output_tokens", 0),
                            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                        }
                        self._log_usage("anthropic", self.config.model, std_usage)
                        
                    return result["content"][0]["text"]
            except Exception as e:
                return f"Error calling Anthropic: {e}"
        elif self.config.provider == "groq":
            api_key = self.config.groq_api_key
            if not api_key:
                return "Error: Groq provider selected but no API key provided (set GROQ_API_KEY)."
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.config.model,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=60.0
                    )
                    result = response.json()
                    if response.status_code != 200:
                        error_msg = result.get("error", {}).get("message", "Unknown error")
                        return f"Error from Groq API ({response.status_code}): {error_msg}"
                    
                    # Log Usage (Groq - same structure as OpenAI)
                    if "usage" in result:
                        self._log_usage("groq", self.config.model, result["usage"])
                        
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error calling Groq: {e}"
        else:
            return f"Error: Unknown LLM provider '{self.config.provider}'."
