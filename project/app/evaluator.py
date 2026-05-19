import os
import csv
import time
from typing import List, Dict

from .decomposition_agent import decompose
from .sql_generator import generate_sql
from .validator import validate_sql
from .executor import run_query
from .retry_agent import retry_generate
from .logger import log_entry


def run_benchmark(input_csv: str, output_csv: str):
    rows = []
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        questions = [r["question"] for r in reader]

    for q in questions:
        start = time.time()
        decomp = {}
        sql = ""
        result = []
        retry_used = False
        status = "failed"
        try:
            decomp = decompose(q)
            sql = generate_sql(decomp)
            ok, msg = validate_sql(sql)
            if not ok:
                status = "invalid_sql"
            else:
                res, err = run_query(sql)
                if err:
                    # attempt one retry
                    retry_used = True
                    sql2 = retry_generate(decomp, sql, err)
                    ok2, msg2 = validate_sql(sql2)
                    if ok2:
                        res2, err2 = run_query(sql2)
                        if err2:
                            status = "failed_after_retry"
                        else:
                            result = res2
                            sql = sql2
                            status = "success_after_retry"
                    else:
                        status = "retry_invalid"
                else:
                    result = res
                    status = "success"
        except Exception as e:
            status = f"error:{e}"

        latency = time.time() - start
        rows.append(
            {
                "question": q,
                "sql_generated": sql,
                "executed_successfully": status.startswith("success"),
                "retry_needed": retry_used,
                "final_status": status,
                "latency": latency,
            }
        )

    # write output CSV
    fieldnames = ["question", "sql_generated", "executed_successfully", "retry_needed", "final_status", "latency"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return rows
