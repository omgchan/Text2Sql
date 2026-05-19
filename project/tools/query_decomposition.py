import json
import os
from typing import Any, Dict, List

import openai


PROMPT = """
You are an assistant that decomposes complex natural language questions about a database
into an ordered set of smaller, answerable sub-questions and corresponding SQL skeletons.

Input: {question}

Output: a JSON object with exactly two keys:
  - "decomposition": an array of short plain-text step descriptions (strings) that explain
    the reasoning or sub-tasks in order.
  - "subqueries": an array of objects, each with keys:
      - "id": integer step id starting at 1
      - "question": the sub-question in plain English
      - "sql_template": a SQL template (use placeholders like <COLUMNS>, <TABLE>, <COND>)

Return ONLY valid JSON. Do not include any surrounding commentary.
"""


def _safe_parse_json(text: str) -> Any:
    """Attempt to extract and parse the first JSON object from text."""
    text = text.strip()
    if not text:
        raise ValueError("Empty response")

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Fallback: find first { and last } and parse substring
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in response")
    sub = text[start : end + 1]
    return json.loads(sub)


def decompose_query(question: str, temperature: float = 0.0) -> Dict[str, Any]:
    """Decompose a natural language SQL question into steps and SQL templates.

    Returns a dict with keys `decomposition` and `subqueries` as described in the prompt.
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise EnvironmentError("OPENAI_API_KEY must be set in environment")

    openai.api_key = openai_key
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    system_msg = (
        "You are an assistant that decomposes complex natural language questions about a database\n"
        "into an ordered set of smaller, answerable sub-questions and corresponding SQL skeletons.\n\n"
        "When given a user question, return ONLY a single JSON object with exactly two keys:\n"
        "- \"decomposition\": an array of short plain-text step descriptions (strings) that explain the reasoning or sub-tasks in order.\n"
        "- \"subqueries\": an array of objects, each with keys:\n"
        "    - \"id\": integer step id starting at 1\n"
        "    - \"question\": the sub-question in plain English\n"
        "    - \"sql_template\": a SQL template (use placeholders like <COLUMNS>, <TABLE>, <COND>)\n\n"
        "Do not include any surrounding commentary or markdown — return valid JSON only."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": question},
    ]

    content = None
    if hasattr(openai, "OpenAI"):
        # Newer openai package (>=1.0.0)
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1024,
        )
        try:
            content = resp["choices"][0]["message"]["content"]
        except Exception:
            content = resp.choices[0].message.content
    elif hasattr(openai, "ChatCompletion"):
        # Older openai package (<1.0.0)
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1024,
        )
        content = resp["choices"][0]["message"]["content"]
    else:
        raise RuntimeError(
            "Installed openai package does not expose ChatCompletion or OpenAI client; please install a compatible version."
        )

    parsed = _safe_parse_json(content)

    # Basic validation/normalization
    if "decomposition" not in parsed or "subqueries" not in parsed:
        raise ValueError("LLM output missing required keys: decomposition or subqueries")

    return parsed


if __name__ == "__main__":
    # Simple CLI demo
    from dotenv import load_dotenv

    load_dotenv()

    sample = (
        "Find the top 5 customers by total purchase amount in 2020, but only include "
        "customers who purchased more than 3 distinct product categories."
    )

    print("Question:", sample)
    try:
        out = decompose_query(sample)
    except Exception as e:
        print("Error:", e)
    else:
        print(json.dumps(out, indent=2))
