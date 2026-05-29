import psycopg2

conn = psycopg2.connect(
    dbname="ppt_database",
    user="user",
    password="password",
    host="localhost",
    port="5434"  
)

cur = conn.cursor()

# Create schema
cur.execute("""
CREATE SCHEMA IF NOT EXISTS ppt_summarizer;
""")

# Table 1: Files
cur.execute("""
CREATE TABLE IF NOT EXISTS ppt_summarizer.files (
    file_id SERIAL PRIMARY KEY,
    file_path TEXT,
    file_extension TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Table 2: Slides (with transcription, summary, and running summary)
cur.execute("""
CREATE TABLE IF NOT EXISTS ppt_summarizer.slide (
    slide_id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL,
    slide_path TEXT,
    slide_transcription TEXT,
    slide_summary TEXT,
    running_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_file
        FOREIGN KEY(file_id)
        REFERENCES ppt_summarizer.files(file_id)
        ON DELETE CASCADE
);
""")

# Table 3: Slide Improvements (scores and suggestions)
cur.execute("""
CREATE TABLE IF NOT EXISTS ppt_summarizer.slide_improvement (
    improvement_id SERIAL PRIMARY KEY,
    slide_id INTEGER NOT NULL,
    
    content_clarity_score FLOAT NOT NULL,
    visual_design_score FLOAT NOT NULL,
    information_density_score FLOAT NOT NULL,
    engagement_score FLOAT NOT NULL,
    overall_score FLOAT NOT NULL,
    
    improvement_points TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_slide
        FOREIGN KEY(slide_id)
        REFERENCES ppt_summarizer.slide(slide_id)
        ON DELETE CASCADE
);
""")

# Table 4: Summary (optional - for overall file summary)
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
