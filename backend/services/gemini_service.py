"""
Centralized Gemini API service layer.
Uses the new google-genai SDK (GA).
Includes retry logic for rate-limit (429) errors.
Logs token usage for cost control and monitoring.
"""

import os
import json
import re
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key or _api_key == "your_gemini_api_key_here":
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Copy backend/.env.example to backend/.env and add your key."
    )

client = genai.Client(api_key=_api_key)

MODEL = "gemini-2.5-flash"

MAX_RETRIES = 3
BASE_DELAY = 10  # seconds


def _log_usage(response, start_time: float):
    """Log token usage and latency from a Gemini response."""
    elapsed = round(time.time() - start_time, 2)
    usage = getattr(response, "usage_metadata", None)

    if usage:
        prompt_tokens = getattr(usage, "prompt_token_count", 0)
        output_tokens = getattr(usage, "candidates_token_count", 0)
        total_tokens = getattr(usage, "total_token_count", 0)

        print(
            f"[Gemini] Model: {MODEL} | "
            f"Prompt: {prompt_tokens} tk | "
            f"Output: {output_tokens} tk | "
            f"Total: {total_tokens} tk | "
            f"Latency: {elapsed}s"
        )
    else:
        print(f"[Gemini] Model: {MODEL} | Latency: {elapsed}s | (no usage metadata)")


def generate_response(system_prompt: str, user_prompt: str) -> str:
    """Send a prompt to Gemini and return the raw text response.
    Retries up to MAX_RETRIES times on rate-limit (429) errors."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            start = time.time()
            response = client.models.generate_content(
                model=MODEL,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=2048,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            _log_usage(response, start)
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


def _safe_json_parse(text: str) -> dict:
    """Parse JSON from model output with fallback regex extraction."""
    # First try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract the first { ... } block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Nothing worked — raise with original text for debugging
    raise ValueError(f"Could not parse JSON from model output: {text[:200]}...")


def generate_json_response(system_prompt: str, user_prompt: str) -> dict:
    """Send a prompt to Gemini and parse the response as JSON."""
    raw = generate_response(system_prompt, user_prompt)

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return _safe_json_parse(cleaned)
