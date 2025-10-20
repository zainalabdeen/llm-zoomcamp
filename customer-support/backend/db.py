import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

PG_URL = os.getenv("POSTGRES_URL")

def get_connection():
    conn = psycopg2.connect(PG_URL)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        question TEXT,
        model_answer TEXT,
        user_feedback TEXT,
        rating INTEGER,
        corrected_answer TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
