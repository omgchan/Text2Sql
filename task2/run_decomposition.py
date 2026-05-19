"""Batch-run the query decomposition over a CSV of questions.

Reads `task2/data/sql_questions_only.csv` (expects a `question` column),
runs `decompose_query` for each row, and writes `decompositions.csv` with
columns: `question`, `decomposition`, `subqueries`, `error`.

Usage:
    python -m task2.run_decomposition --input task2/data/sql_questions_only.csv --output task2/data/decompositions.csv
"""

import argparse
import json
import os
from typing import Dict, Any

import pandas as pd

from task2.query_decomposition import decompose_query


def run(input_csv: str, output_csv: str, temperature: float = 0.0) -> None:
    df = pd.read_csv(input_csv)
    if "question" not in df.columns:
        raise ValueError("Input CSV must contain a 'question' column")

    rows = []
    total = len(df)
    for i, q in enumerate(df["question"].fillna(""), start=1):
        print(f"[{i}/{total}] Processing question: {q}")
        try:
            parsed = decompose_query(q, temperature=temperature)
            decomposition = parsed.get("decomposition")
            subqueries = parsed.get("subqueries")
            rows.append(
                {
                    "question": q,
                    "decomposition": json.dumps(decomposition, ensure_ascii=False),
                    "subqueries": json.dumps(subqueries, ensure_ascii=False),
                    "error": "",
                }
            )
        except Exception as e:
            rows.append({"question": q, "decomposition": "", "subqueries": "", "error": str(e)})

    out_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    out_df.to_csv(output_csv, index=False)
    print(f"Wrote {len(out_df)} rows to {output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", default="task2/data/sql_questions_only.csv")
    parser.add_argument("--output", "-o", default="task2/data/decompositions.csv")
    parser.add_argument("--temperature", "-t", type=float, default=0.0)
    args = parser.parse_args()
    run(args.input, args.output, temperature=args.temperature)


if __name__ == "__main__":
    main()
