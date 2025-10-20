from .db import get_connection
import pandas as pd
from datetime import datetime


def save_feedback(query, answer, feedback, rating):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            query TEXT,
            answer TEXT,
            feedback TEXT,
            rating INT,
            created_at TIMESTAMP
        )
    """)
    cur.execute("""
        INSERT INTO feedback (query, answer, feedback, rating, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (query, answer, feedback, rating, datetime.utcnow()))
    conn.commit()
    cur.close()
    conn.close()


def load_feedback_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM feedback ORDER BY timestamp DESC", conn)
    conn.close()
    return df
