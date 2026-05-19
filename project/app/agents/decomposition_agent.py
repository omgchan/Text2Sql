import os
import json
from typing import Dict, Any

import openai

PROMPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "decomposition_prompt.txt"))


def _load_prompt() -> str:
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return (
            "Decompose the user question into JSON with keys: intent, tables, columns, filters, joins."
            " Do not produce SQL. Use database reasoning and do NOT hallucinate schema. Return only JSON."
        )


def decompose(question: str, temperature: float = 0.0) -> Dict[str, Any]:
    """Produce a structured decomposition for a question.

    Uses OpenAI SDK. For production you can replace with LangChain pipelines.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY required")
    openai.api_key = key

    prompt = _load_prompt()
    system_msg = prompt
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": question},
    ]

    model = os.environ.get("OPENAI_MODEL", "gpt-4")
    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI()
        resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        content = resp["choices"][0]["message"]["content"]
    else:
        resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
        content = resp["choices"][0]["message"]["content"]

    content = content.strip()
    try:
        return json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Failed to parse decomposition JSON")
        return json.loads(content[start : end + 1])
