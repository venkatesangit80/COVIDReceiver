import sqlite3

# Database path
DB_PATH = "/mnt/data/ai_security_recommendations.db"

def create_ai_and_security_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 5. AI Chatbot Interaction Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            user_query TEXT,
            ai_response TEXT,
            feedback TEXT,
            context_summary TEXT,
            ai_accuracy_rating INTEGER  -- scale of 1 to 5
        )
    """)

    # 6. Contextual Recommendation Data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            related_incident_id INTEGER,
            recommendation TEXT,
            resolution_accuracy TEXT,
            engineer_feedback TEXT,
            correlation_reason TEXT,
            success_rate REAL  -- e.g., 0.85 for 85%
        )
    """)

    # 7. Security & Compliance Data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            system_accessed TEXT,
            access_type TEXT,  -- e.g., login, modify, delete
            role TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_compliance_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT,
            security_incident_summary TEXT,
            resolution_details TEXT,
            policy_enforced TEXT
        )
    """)

    conn.commit()
    conn.close()

# Run once
create_ai_and_security_tables()

DB_PATH
