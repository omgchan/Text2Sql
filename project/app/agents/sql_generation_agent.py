import os
import json
import openai
from typing import Dict, Any

PROMPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "sql_generation_prompt.txt"))


def _load_prompt() -> str:
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Given decomposition JSON, produce a single valid PostgreSQL SELECT statement. Return only SQL."


def generate(decomposition: Dict[str, Any], temperature: float = 0.0) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY required")
    openai.api_key = key

    prompt = _load_prompt()
    content = f"Decomposition: {json.dumps(decomposition)}\n\n{prompt}"
    model = os.environ.get("OPENAI_MODEL", "gpt-4")

    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI()
        resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":content}], temperature=temperature)
        sql = resp["choices"][0]["message"]["content"]
    else:
        resp = openai.ChatCompletion.create(model=model, messages=[{"role":"user","content":content}], temperature=temperature)
        sql = resp["choices"][0]["message"]["content"]

    sql = sql.strip().strip('`')
    return sql
