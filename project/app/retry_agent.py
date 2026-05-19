import os
import json
import openai
from typing import Dict, Any

PROMPT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts", "retry_prompt.txt"))


def _load_prompt() -> str:
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return (
            "Given the decomposition, the previously generated SQL, and the database error,"
            " generate a corrected PostgreSQL SELECT statement. Return ONLY the SQL."
        )


def retry_generate(decomposition: Dict[str, Any], previous_sql: str, error: str, temperature: float = 0.0) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY required")
    openai.api_key = key

    prompt = _load_prompt()
    content = (
        f"Decomposition: {json.dumps(decomposition)}\nPrevious SQL: {previous_sql}\nError: {error}\n\n{prompt}"
    )
    model = os.environ.get("OPENAI_MODEL", "gpt-4")

    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI()
        resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":content}], temperature=temperature)
        sql = resp["choices"][0]["message"]["content"]
    else:
        resp = openai.ChatCompletion.create(model=model, messages=[{"role":"user","content":content}], temperature=temperature)
        sql = resp["choices"][0]["message"]["content"]

    return sql.strip().strip('`')
