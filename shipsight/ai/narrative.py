import httpx
from typing import Optional
from rich.console import Console

from shipsight.config import AIConfig

console = Console()

class NarrativeGenerator:
    def __init__(self, config: AIConfig):
        self.config = config

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
        guidelines = "- Hook: A punchy benefit."
        if dna == "MOBILE":
            guidelines = "- Hook: Focus on the 'App Experience' or 'Utility on the go'.\n- Use mobile terms: 'Tap', 'Swipe', 'Pocket-sized power'."
        elif dna == "CLI":
            guidelines = "- Hook: Focus on 'Speed', 'Automation', or 'Saving Developer Time'.\n- Use dev terms: 'Terminal', 'Workflow', 'Pipeline'."
            
        prompt = f"""
        Generate a "Feature Showcase" LinkedIn post.
        
        CONTEXT:
        {context}
        
        TASK:
        1. Analyze the features in the context.
        2. Pick the top 3 most impressive features.
        3. Write a viral LinkedIn post using the persona of a {dna} Expert.
        
        GUIDELINES:
        {guidelines}
        - Tone: Energetic, innovative, less 'corporate', more 'builder'.
        - NO EMOJIS.
        - Bottom line: Mention TECH STACK (e.g. Built with Flutter 💙).
        
        ### ANTI-HALLUCINATION:
        - If the app is named 'LenghtEverything', it is about MEASURING LENGTHS. It is NOT about SEO, Roasting, or Websites.
        - DO NOT invent features not in the context.
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
                    return response.json().get("response", "Error: LLM failed to respond.")
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
                        
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error calling Groq: {e}"
        else:
            return f"Error: Unknown LLM provider '{self.config.provider}'."
