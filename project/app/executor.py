from .database import execute_sql


def run_query(sql: str):
    rows, err = execute_sql(sql)
    if err:
        return None, err
    return rows, None
