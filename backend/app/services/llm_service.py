"""
LLM Service — Gemini 2.5 Flash / Pro tier routing.

Two tiers:
  Flash → High-frequency tasks: question generation, technical eval, communication eval.
  Pro   → Final report and executive summary only (higher quality, higher cost).

Usage:
    LLMService(task="eval")   → Flash
    LLMService(task="report") → Pro
"""
import json
from typing import Dict, Any, Optional
from app.core.config import get_settings
import os

settings = get_settings()

# Push API keys into env so LiteLLM/google-genai picks them up
if settings.gemini_api_key:
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key


# Model tier definitions
FLASH_MODEL = "gemini/gemini-2.5-flash"    # All evaluations, question gen, coaching
PRO_MODEL   = "gemini/gemini-2.5-pro"      # Executive summary + final report only

# Fallback chain when primary fails
FALLBACK_CHAIN = [
    "gemini/gemini-2.0-flash",
    "gpt-4o-mini",
    "claude-3-5-haiku-20241022",
]


class LLMService:
    def __init__(self, task: str = "eval", provider: Optional[str] = None):
        """
        task: "eval"   → Gemini 2.5 Flash (fast, cost-efficient)
              "report" → Gemini 2.5 Pro  (high quality, final output only)
        """
        if task == "report":
            self.model = PRO_MODEL
        else:
            self.model = FLASH_MODEL

        # Allow explicit provider override for testing
        if provider:
            self.model = self._get_legacy_model(provider)

    def _get_legacy_model(self, provider: str) -> str:
        """Backwards compatibility with old provider strings."""
        legacy = {
            "openai": "gpt-4o",
            "gemini": FLASH_MODEL,
            "anthropic": "claude-3-5-sonnet-20240620",
        }
        return legacy.get(provider.lower(), FLASH_MODEL)

    async def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate plain text from LLM."""
        from litellm import completion
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            # Try fallback models
            for fallback in FALLBACK_CHAIN:
                try:
                    response = completion(
                        model=fallback,
                        messages=messages,
                        temperature=temperature,
                    )
                    return response.choices[0].message.content
                except Exception:
                    continue
            raise RuntimeError(f"All LLM models failed. Last error: {e}")

    async def generate_json(self, prompt: str, system_prompt: str = "", temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate structured JSON from LLM.
        Enforces JSON-only output via system prompt instruction.
        Falls back to manual extraction if model wraps in markdown.
        """
        if not system_prompt:
            system_prompt = "You are a helpful assistant."

        system_prompt += (
            "\n\nCRITICAL: You must respond ONLY with a valid JSON object. "
            "Do not include any markdown, code fences, or extra text."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        from litellm import completion
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
        except Exception as e:
            # Fallback without json_object mode (some models don't support it)
            try:
                response = completion(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                )
                content = response.choices[0].message.content
            except Exception:
                raise RuntimeError(f"LLM call failed: {e}")

        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        """Strip markdown fences and parse JSON."""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM JSON response: {content[:200]}") from e
