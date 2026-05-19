import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agents.decomposition_agent import decompose
from .agents.sql_generation_agent import generate
from .validator import validate_sql
from .executor import run_query
from .agents.retry_agent import generate_fix
from .agents.summary_agent import summarize
from .logger import log_entry


class QueryIn(BaseModel):
    question: str
    temperature: float = 0.0


app = FastAPI(title="Agentic Text-to-SQL")


@app.post("/agent/sql")
def run_agent_sql(payload: QueryIn):
    q = payload.question
    temp = payload.temperature
    retry_count = 0
    max_retries = int(os.environ.get("MAX_RETRIES", 3))

    try:
        decomposition = decompose(q, temperature=temp)
    except Exception as e:
        log_entry({"question": q, "error": f"decompose_failed: {e}", "status": "failed"})
        raise HTTPException(status_code=400, detail=f"Decomposition failed: {e}")

    try:
        sql = generate(decomposition, temperature=temp)
    except Exception as e:
        log_entry({"question": q, "decomposition": decomposition, "error": f"generate_failed: {e}", "status": "failed"})
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {e}")

    ok, msg = validate_sql(sql)
    if not ok:
        log_entry({"question": q, "decomposition": decomposition, "sql": sql, "error": f"validation_failed: {msg}", "status": "failed"})
        raise HTTPException(status_code=400, detail=f"Validation failed: {msg}")

    final_result = []
    status = "failed"
    execution_time = None
    last_error = ""

    while True:
        import time

        start = time.time()
        result, err = run_query(sql)
        execution_time = time.time() - start
        if err:
            last_error = err
            retry_count += 1
            log_entry({"question": q, "decomposition": decomposition, "sql": sql, "error": err, "retry": retry_count})
            if retry_count > max_retries:
                status = "failed"
                break
            # attempt to fix SQL
            try:
                sql = generate_fix(decomposition, sql, err)
            except Exception as e:
                last_error = str(e)
                break
            ok2, msg2 = validate_sql(sql)
            if not ok2:
                last_error = msg2
                break
            # loop to retry execution
            continue
        else:
            final_result = result
            status = "success"
            break

    if status != "success":
        log_entry({"question": q, "decomposition": decomposition, "sql": sql, "status": status, "last_error": last_error, "retry_count": retry_count})
        return {
            "status": "failed",
            "message": "Unable to generate valid SQL after multiple attempts.",
            "last_error": last_error,
        }

    # generate natural language summary
    try:
        summary = summarize(q, decomposition, final_result)
    except Exception:
        summary = ""

    entry = {
        "question": q,
        "decomposition": decomposition,
        "sql": sql,
        "result": final_result,
        "summary": summary,
        "retry_count": retry_count,
        "execution_time": execution_time,
        "status": status,
    }
    log_entry(entry)
    return entry
