import os
import json
import openai
from typing import Any, Dict

PROMPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "summary_prompt.txt"))


def _load_prompt() -> str:
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Given the question, decomposition, and SQL result, produce a concise human-readable summary that accurately reflects the result. Return only the summary sentence."


def summarize(question: str, decomposition: Dict[str, Any], result: Any, temperature: float = 0.0) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY required")
    openai.api_key = key

    prompt = _load_prompt()
    content = (
        f"Question: {question}\nDecomposition: {json.dumps(decomposition)}\nResult: {json.dumps(result)}\n\n{prompt}"
    )
    model = os.environ.get("OPENAI_MODEL", "gpt-4")

    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI()
        resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":content}], temperature=temperature)
        summary = resp["choices"][0]["message"]["content"]
    else:
        resp = openai.ChatCompletion.create(model=model, messages=[{"role":"user","content":content}], temperature=temperature)
        summary = resp["choices"][0]["message"]["content"]

    return summary.strip().strip('"')
