"""
Migration script to add slide_transcription column to existing databases.

Run this if you have an existing database with data and want to add the new column.
"""

import psycopg2

conn = psycopg2.connect(
    dbname="ppt_database",
    user="user",
    password="password",
    host="localhost",
    port="5434"
)

cur = conn.cursor()

# Add slide_transcription column if it doesn't exist
cur.execute("""
ALTER TABLE ppt_summarizer.slide
ADD COLUMN IF NOT EXISTS slide_transcription TEXT;
""")

print("Successfully added slide_transcription column to ppt_summarizer.slide table")
print("Note: Existing rows will have NULL in slide_transcription column")

conn.commit()
cur.close()
conn.close()
