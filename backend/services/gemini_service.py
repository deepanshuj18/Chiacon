"""
Centralized Gemini API service layer.
Reuses a single model instance for all requests.
Includes retry logic for rate-limit (429) errors.
"""

import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key or _api_key == "your_gemini_api_key_here":
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Copy backend/.env.example to backend/.env and add your key."
    )

genai.configure(api_key=_api_key)

_model = genai.GenerativeModel("gemini-2.0-flash")

MAX_RETRIES = 3
BASE_DELAY = 10  # seconds


def generate_response(system_prompt: str, user_prompt: str) -> str:
    """Send a prompt to Gemini and return the raw text response.
    Retries up to MAX_RETRIES times on rate-limit (429) errors."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = _model.generate_content(
                [
                    {"role": "user", "parts": [f"{system_prompt}\n\n{user_prompt}"]},
                ],
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                ),
            )
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e)
            # Retry only on rate-limit errors
            if "429" in error_str or "quota" in error_str.lower():
                if attempt < MAX_RETRIES:
                    wait = BASE_DELAY * (2 ** attempt)
                    print(f"[Gemini] Rate limited. Retrying in {wait}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(wait)
                    continue
            # Non-retryable error — raise immediately
            raise
    raise last_error


def generate_json_response(system_prompt: str, user_prompt: str) -> dict:
    """Send a prompt to Gemini and parse the response as JSON."""
    raw = generate_response(system_prompt, user_prompt)

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (the fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return json.loads(cleaned)
