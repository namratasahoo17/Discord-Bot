import os
import json

from google import genai

from .prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in .env"
    )


client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# AI ANALYSIS
# ============================================================

async def analyze_student(data):
    """
    Analyze a student's study data using Gemini.
    """

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

