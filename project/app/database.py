import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    params = dict(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", 5432)),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
        dbname=os.environ.get("PGDATABASE", "postgres"),
    )
    conn = psycopg2.connect(**params)
    return conn


def execute_sql(sql: str, params=None, timeout: int = 30):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        # Only allow SELECTs to fetch results
        if cur.description:
            rows = cur.fetchall()
        else:
            rows = []
        cur.close()
        conn.commit()
        return rows, None
    except Exception as e:
        if conn:
            conn.rollback()
        return None, str(e)
    finally:
        if conn:
            conn.close()
