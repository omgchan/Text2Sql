import re


FORBIDDEN = [r"\bDELETE\b", r"\bDROP\b", r"\bUPDATE\b", r"\bINSERT\b", r"\bALTER\b", r"\bTRUNCATE\b"]


def validate_sql(sql: str) -> (bool, str):
    s = sql.strip()
    # Only allow SELECT queries
    if not re.match(r"(?i)^\s*SELECT\b", s):
        return False, "Only SELECT queries are allowed"

    # For safety, disallow semicolons followed by anything (prevent stacked queries)
    if ";" in s and not s.rstrip().endswith(";"):
        return False, "Multiple statements or trailing content detected"

    # Forbidden keywords
    for pat in FORBIDDEN:
        if re.search(pat, s, flags=re.IGNORECASE):
            return False, f"Forbidden SQL operation detected: {pat}"

    return True, "ok"
