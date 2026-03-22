import psycopg2
import os

conn = psycopg2.connect(
    dbname="ppt_database",
    user="user",
    password="password",
    host="localhost",
    port="5434"  
)

cur = conn.cursor()

cur.execute("""
CREATE SCHEMA IF NOT EXISTS ppt_summarizer;
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ppt_summarizer.files (
    file_id SERIAL PRIMARY KEY,
    file_path TEXT,
    file_extension TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ppt_summarizer.slide (
    slide_id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL,
    slide_path TEXT,
    slide_summary TEXT,
    running_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_file
        FOREIGN KEY(file_id)
        REFERENCES ppt_summarizer.files(file_id)
        ON DELETE CASCADE
);
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS ppt_summarizer.summary (
    summary_id SERIAL PRIMARY KEY,
    file_id INTEGER,
    summary_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_file_summary
        FOREIGN KEY(file_id)
        REFERENCES ppt_summarizer.files(file_id)
        ON DELETE CASCADE

);
""")


conn.commit()
cur.close()
conn.close()
