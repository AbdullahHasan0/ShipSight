import httpx
from typing import Optional
from rich.console import Console

from shipsight.config import AIConfig

console = Console()

class NarrativeGenerator:
    def __init__(self, config: AIConfig):
        self.config = config

    async def generate_readme(self, context: str, heroes: dict = None) -> str:
        prompt = f"""
        Act as a Product Manager / Lead Engineer. Generate a professional README.md focused on FEATURES and USER VALUE.
        
        {context}
        
        ### STRICT CONTEXT PURITY RULES:
        - ONLY use information provided in the CONTEXT above.
        - DO NOT HALLUCINATE features like "Website Roasting", "SEO Analysis", or "Auth Systems" unless they are explicitly mentioned in the context.
        - If the project is about measurements or lengths, STAY ON TOPIC.
        - Focus on "What the project does", "Key Features", and "How to use it".
        - DO NOT use emojis anywhere in the README.
        """
        return await self._call_llm(prompt)

    async def generate_linkedin_post(self, context: str) -> str:
        prompt = f"""
        Generate a "Feature Showcase" LinkedIn post. Focus on REAL-WORLD CAPABILITIES and IMPACT.
        
        {context}
        
        ### ANTI-HALLUCINATION GUARDRAILS:
        - NEVER mention features from previous projects (e.g., SEO, Roasters, A/B testing) if they are not in the context.
        - Use the PHILOSOPHY and CORE GOAL sections from the context to find the "Soul" of this project.
        - If the project name is "LenghtEverything", talk about LENGTHS and VISUALIZATION, not websites.
        
        Guidelines for a VIRAL Showcase Post:
        - Hook: A punchy benefit (e.g., "Ever wondered how long a blue whale really is?").
        - List 3 unique features found in the context.
        - Tone: Energetic, innovative, result-oriented, enthusiastic, less 'engineer', more 'creator'.
        - Mention the TECH STACK briefly at the bottom.
        - DO NOT use emojis anywhere in the post.
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
