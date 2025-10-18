import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen3-235b-a22b-2507"  # Make sure this model exists in your OpenRouter account


def generate_from_paragraph(paragraph: str, num_questions: int = 1):
    """
    Generate multiple-choice questions (MCQs) from a paragraph.
    Returns a list of dicts with 'question', 'choices', 'answer', 'explanation'.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("Missing OPENROUTER_API_KEY")

    mcqs = []

    for _ in range(num_questions):
        # Prompt with proper JSON formatting (comma added)
        prompt = f"""
You are a study question generator.
Generate ONE multiple-choice question (with 4 options) from the following paragraph.
Include an explanation for why the correct answer is correct.
Respond in JSON format exactly like this:
{{
  "mcq": {{
    "question": "...",
    "choices": ["A", "B", "C", "D"],
    "answer": "...",
    "explanation": "..."
  }}
}}
Paragraph:
{paragraph}
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You generate study questions."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter error: {response.status_code} - {response.text}")

        # Parse JSON safely
        try:
            content = response.json()["choices"][0]["message"]["content"]
            # Attempt to extract JSON from content
            match = re.search(r"\{.*\}", content, re.S)
            if not match:
                print("⚠️ No JSON found in response:", content)
                continue
            mcq_data = json.loads(match.group(0)).get("mcq")
            if mcq_data:
                mcqs.append(mcq_data)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print("⚠️ Parse error:", e)
            print("Raw output:", response.text)
            continue

    return mcqs
