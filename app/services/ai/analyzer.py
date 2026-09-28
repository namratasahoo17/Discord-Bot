import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from .prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)


# ============================================================
# FIND PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"

print(f"[AI] Looking for .env at: {ENV_FILE}")
print(f"[AI] .env exists: {ENV_FILE.exists()}")


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY")


print(
    f"[AI] Gemini API key: "
    f"{'FOUND' if API_KEY else 'NOT FOUND'}"
)


# ============================================================
# CHECK API KEY
# ============================================================

if not API_KEY:
    raise RuntimeError(
        f"GEMINI_API_KEY was not found.\n"
        f"Expected .env location:\n"
        f"{ENV_FILE}"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# ANALYZE STUDENT
# ============================================================

async def analyze_student(data):

    prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + build_analysis_prompt(data)
    )

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    result = response.text

    return json.loads(result)