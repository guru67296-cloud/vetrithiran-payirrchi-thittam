from __future__ import annotations

from google import genai
from google.genai import types

from ..config import get_settings


SAFETY_NOTE = (
    "Safety note: This is general wellness information, not medical advice. "
    "Do not diagnose conditions, prescribe medication, or recommend unsafe/extreme exercise. "
    "Include reasonable warm-up, recovery, hydration, and rest guidance."
)


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = (
            genai.Client(api_key=self.settings.gemini_api_key)
            if self.settings.gemini_api_key
            else None
        )

    @property
    def available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str, model: str) -> str:
        if not self.client:
            if self.settings.ai_fallback_enabled:
                return ""
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=2500,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text


gemini_service = GeminiService()
