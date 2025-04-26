# --- Database.py ---
import sqlite3
import os

db_path = "legal_analysis.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS document_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    summary TEXT,
    key_clauses TEXT,
    risks TEXT,
    compliance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

def store_analysis(filename, analysis):
    cursor.execute('''
        INSERT INTO document_analysis (filename, summary, key_clauses, risks, compliance)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        filename,
        analysis.get("summary", ""),
        str(analysis.get("key_clauses", "")),
        str(analysis.get("risks", "")),
        str(analysis.get("compliance", ""))
    ))
    conn.commit()

def fetch_recent_analyses(limit=5):
    cursor.execute('''
        SELECT filename, summary, key_clauses, risks, compliance, created_at
        FROM document_analysis
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    return [
        {
            "filename": r[0],
            "summary": r[1],
            "key_clauses": r[2],
            "risks": r[3],
            "compliance": r[4],
            "created_at": r[5]
        } for r in rows
    ]
