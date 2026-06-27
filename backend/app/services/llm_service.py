"""
LLM Gateway — Centralized LLM routing and Structured Output Validation.
"""
import os
import json
import time
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from litellm import completion
from app.core.config import get_settings

settings = get_settings()

if settings.gemini_api_key:
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

FLASH_MODEL = "gemini/gemini-2.5-flash"

T = TypeVar('T', bound=BaseModel)

class LLMGateway:
    """
    Central gateway for all LLM calls.
    Handles retries, fallbacks, and strictly validates structured output against Pydantic models.
    """
    def __init__(self, model: str = FLASH_MODEL):
        self.model = model
        self.max_retries = 3

    async def generate_structured(
        self, 
        prompt: str, 
        response_model: Type[T], 
        system_prompt: str = ""
    ) -> T:
        """
        Calls the LLM and strictly validates the output against the provided Pydantic model.
        Automatically retries on hallucinated schemas.
        """
        if not system_prompt:
            system_prompt = "You are a helpful assistant."
            
        system_prompt += (
            f"\n\nCRITICAL: You must respond ONLY with a valid JSON object matching this schema:\n"
            f"{json.dumps(response_model.model_json_schema(), indent=2)}\n"
            f"Do not include markdown or extra text."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = completion(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content.strip()
                
                # Strip potential markdown fences
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                content = content.strip()
                
                # Validate against Pydantic model
                return response_model.model_validate_json(content)
                
            except ValidationError as e:
                last_error = e
                print(f"[LLMGateway] Schema validation failed on attempt {attempt+1}: {e}")
                # Append error to messages to self-correct
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": f"Your JSON failed validation: {e}. Fix the structure."})
                time.sleep(1)
            except Exception as e:
                last_error = e
                print(f"[LLMGateway] API error on attempt {attempt+1}: {e}")
                time.sleep(2)
                
        raise RuntimeError(f"LLMGateway failed to generate valid structured output after {self.max_retries} attempts. Last error: {last_error}")

    async def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
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
            raise RuntimeError(f"LLM call failed: {e}")
