"""
How it works: Each time run_once() is called, it will connect to the database, create the tables if needed, 
insert five new random incident records, possibly link two of them as parent/child, and then archive+delete any incidents older than 5 hours. 
You can schedule this function to run every 5 minutes (using cron or a similar scheduler). Over time, the incident_tickets table will only 
contain recent incidents (last 5 hours), while older ones accumulate in historical_incidents. The incident_dependencies table maintains 
relationships among active tickets (any relations involving an incident are cleaned up once that incident ages out and is removed from the 
main table).

Save this script as a .py file and ensure it has execute permissions if needed. You can then set up a cron job (for example, using */5 * * * * python /path/to/incident_manager.py) to run it every 5 minutes.
"""


import sqlite3
import random
from datetime import datetime, timedelta

def run_once():
    """Execute one cycle of incident generation and cleanup."""
    # Connect to the SQLite database (will be created if it doesn't exist)
    conn = sqlite3.connect("/mnt/data/incident_management.db")
    cursor = conn.cursor()
    # Ensure foreign key support is enabled (for cascading deletes in dependencies)
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create the incident_tickets table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application TEXT,
            server TEXT,
            error_type TEXT,
            issue_summary TEXT,
            priority TEXT,
            category TEXT,
            status TEXT,
            resolution_time TEXT,
            rca_notes TEXT,
            created_at TEXT
        )
    """)
    # Create the historical_incidents table (to archive old incidents)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_ticket_id INTEGER,
            application TEXT,
            server TEXT,
            error_type TEXT,
            issue_summary TEXT,
            priority TEXT,
            category TEXT,
            status TEXT,
            resolution_time TEXT,
            rca_notes TEXT,
            created_at TEXT
            -- Optionally, you can add: FOREIGN KEY(original_ticket_id) REFERENCES incident_tickets(id)
        )
    """)
    # Create the incident_dependencies table (to store parent-child relations between tickets)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            child_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES incident_tickets(id) ON DELETE CASCADE,
            FOREIGN KEY(child_id) REFERENCES incident_tickets(id) ON DELETE CASCADE
        )
    """)
    
    # Predefined values for random selection
    applications = ["InventorySystem", "OrderService", "WebPortal", "AnalyticsApp", "HRTool"]
    servers = [f"Server-{i:02d}" for i in range(1, 51)]  # Server-01 to Server-50
    error_types = ["Infrastructure", "Application"]
    categories_infra = ["Network", "Server", "Database"]
    categories_app = ["API", "Database", "UI"]
    priorities = ["Low", "Medium", "High"]
    # Example issue summaries for each category
    summaries_by_category = {
        "Network": [
            "Network latency is high",
            "Packet loss detected in network",
            "DNS resolution failure"
        ],
        "Server": [
            "Server is not responding",
            "Server CPU usage is 100%",
            "Server ran out of memory"
        ],
        "Database": [
            "Database connection timeout",
            "Slow database query execution",
            "Database server not reachable"
        ],
        "API": [
            "API is returning 500 errors",
            "Null pointer exception in API",
            "API response time is very slow"
        ],
        "UI": [
            "Frontend UI is not loading",
            "UI throwing a JavaScript error",
            "Layout issue on dashboard page"
        ]
    }
    
    # Insert multiple new incident tickets (e.g., 5 incidents per run)
    new_ticket_ids = []
    for _ in range(5):
        app = random.choice(applications)
        server = random.choice(servers)
        error_type = random.choice(error_types)
        # Pick a category based on error type
        if error_type == "Infrastructure":
            category = random.choice(categories_infra)
        else:
            category = random.choice(categories_app)
        # Choose an issue summary relevant to the category (fallback to generic if not found)
        if category in summaries_by_category:
            issue_summary = random.choice(summaries_by_category[category])
        else:
            issue_summary = "General system error"
        priority = random.choice(priorities)
        # Determine status and resolution details
        if random.random() < 0.3:  # 30% chance the incident is already resolved
            status = "Resolved"
            resolution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rca_notes = "Issue resolved after troubleshooting."
        else:
            status = "Open"
            resolution_time = None
            rca_notes = None
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Insert the new incident record
        cursor.execute(
            "INSERT INTO incident_tickets (application, server, error_type, issue_summary, priority, category, status, resolution_time, rca_notes, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (app, server, error_type, issue_summary, priority, category, status, resolution_time, rca_notes, created_at)
        )
        # Capture the new ticket's ID for potential dependency linking
        new_ticket_ids.append(cursor.lastrowid)
    
    # Optionally create a random dependency between two of the new incidents
    if len(new_ticket_ids) >= 2:
        parent_id = random.choice(new_ticket_ids)
        # Ensure child_id is different from parent_id
        possible_children = [tid for tid in new_ticket_ids if tid != parent_id]
        if possible_children:
            child_id = random.choice(possible_children)
            cursor.execute(
                "INSERT INTO incident_dependencies (parent_id, child_id) VALUES (?, ?)",
                (parent_id, child_id)
            )
    
    # Commit the new insertions
    conn.commit()
    
    # Implement retention policy: archive and delete incidents older than 5 hours
    cutoff_time = datetime.now() - timedelta(hours=5)
    cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")
    # Find all incident tickets older than the cutoff
    cursor.execute("SELECT * FROM incident_tickets WHERE created_at < ?", (cutoff_str,))
    old_incidents = cursor.fetchall()
    if old_incidents:
        for incident in old_incidents:
            incident_id = incident[0]  # id is the first column in incident_tickets
            # Copy the old incident into historical_incidents
            cursor.execute(
                "INSERT INTO historical_incidents (original_ticket_id, application, server, error_type, issue_summary, priority, category, status, resolution_time, rca_notes, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    incident_id,
                    incident[1],  # application
                    incident[2],  # server
                    incident[3],  # error_type
                    incident[4],  # issue_summary
                    incident[5],  # priority
                    incident[6],  # category
                    incident[7],  # status
                    incident[8],  # resolution_time
                    incident[9],  # rca_notes
                    incident[10]  # created_at
                )
            )
            # Delete any dependency records linked to this incident
            cursor.execute("DELETE FROM incident_dependencies WHERE parent_id = ? OR child_id = ?", (incident_id, incident_id))
        # Remove the old incidents from the main table
        cursor.execute("DELETE FROM incident_tickets WHERE created_at < ?", (cutoff_str,))
    
    # Commit the archival and deletions
    conn.commit()
    conn.close()

# If the script is run directly, execute one cycle
if __name__ == "__main__":
    run_once()
