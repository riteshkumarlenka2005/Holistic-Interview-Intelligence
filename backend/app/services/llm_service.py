import json
from typing import Dict, Any, Optional, List
from litellm import completion
from app.core.config import get_settings
import os

settings = get_settings()

# Set API keys for LiteLLM from settings
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
if settings.gemini_api_key:
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key

class LLMService:
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM service. 
        Provider can be 'openai', 'gemini', 'anthropic', etc.
        Falls back to settings.ai_provider if not specified.
        """
        self.provider = provider or settings.ai_provider
        self.model = self._get_default_model(self.provider)

    def _get_default_model(self, provider: str) -> str:
        models = {
            "openai": "gpt-4o",
            "gemini": "gemini/gemini-1.5-pro",
            "anthropic": "claude-3-5-sonnet-20240620"
        }
        return models.get(provider.lower(), "gpt-4o")

    async def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate plain text from LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = completion(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content

    async def generate_json(self, prompt: str, system_prompt: str = "", temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate structured JSON from LLM.
        Appends a JSON instruction to the system prompt and uses JSON mode if supported.
        """
        if not system_prompt:
            system_prompt = "You are a helpful assistant."
            
        system_prompt += "\n\nIMPORTANT: You must respond ONLY with a valid JSON object. Do not include markdown code blocks like ```json."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        try:
            # Strip markdown if model still included it
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM JSON response: {content}") from e
