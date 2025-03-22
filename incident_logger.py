import sqlite3
import os
import time
import random
from datetime import datetime, timedelta

# Database configuration
DB_PATH = "/mnt/data/incident_management.db"
RETENTION_HOURS = 5
INSERT_INTERVAL_SECONDS = 5 * 60  # 5 minutes

# Ensure database and tables exist
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create main incident ticket table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_summary TEXT,
            priority TEXT,
            category TEXT,
            status TEXT,
            resolution_time INTEGER,
            rca_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create historical incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_incidents (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            timestamp TEXT,
            resolution_steps TEXT,
            assigned_engineer TEXT,
            FOREIGN KEY(ticket_id) REFERENCES incident_tickets(ticket_id)
        )
    """)

    # Create incident dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_dependencies (
            dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_ticket_id INTEGER,
            child_ticket_id INTEGER,
            FOREIGN KEY(parent_ticket_id) REFERENCES incident_tickets(ticket_id),
            FOREIGN KEY(child_ticket_id) REFERENCES incident_tickets(ticket_id)
        )
    """)

    conn.commit()
    conn.close()

# Generate and insert random incident data
def insert_incident_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    priorities = ['High', 'Medium', 'Low']
    categories = ['Network', 'Server', 'Application', 'Security']
    statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    engineers = ['Alice', 'Bob', 'Charlie', 'David']

    issue_summary = f"Issue {random.randint(1000, 9999)}"
    priority = random.choice(priorities)
    category = random.choice(categories)
    status = random.choice(statuses)
    resolution_time = random.randint(10, 180) if status == 'Resolved' else None
    rca_notes = "Root cause identified and resolved." if resolution_time else ""
    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Insert into incident_tickets
    cursor.execute("""
        INSERT INTO incident_tickets (issue_summary, priority, category, status, resolution_time, rca_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (issue_summary, priority, category, status, resolution_time, rca_notes, created_at))
    ticket_id = cursor.lastrowid

    # Insert into historical_incidents
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    resolution_steps = "Rebooted service and cleared logs."
    assigned_engineer = random.choice(engineers)
    cursor.execute("""
        INSERT INTO historical_incidents (ticket_id, timestamp, resolution_steps, assigned_engineer)
        VALUES (?, ?, ?, ?)
    """, (ticket_id, timestamp, resolution_steps, assigned_engineer))

    # Optionally insert into dependencies with a chance
    if random.random() < 0.5:
        related_ticket = ticket_id - random.randint(1, 5)
        if related_ticket > 0:
            cursor.execute("""
                INSERT INTO incident_dependencies (parent_ticket_id, child_ticket_id)
                VALUES (?, ?)
            """, (related_ticket, ticket_id))

    conn.commit()
    conn.close()

# Remove data older than retention period
def rotate_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_time = datetime.utcnow() - timedelta(hours=RETENTION_HOURS)
    cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

    # Delete from dependencies first to avoid FK constraint issues
    cursor.execute("""
        DELETE FROM incident_dependencies
        WHERE parent_ticket_id IN (
            SELECT ticket_id FROM incident_tickets WHERE created_at < ?
        ) OR child_ticket_id IN (
            SELECT ticket_id FROM incident_tickets WHERE created_at < ?
        )
    """, (cutoff_str, cutoff_str))

    # Delete from historical_incidents
    cursor.execute("""
        DELETE FROM historical_incidents
        WHERE ticket_id IN (
            SELECT ticket_id FROM incident_tickets WHERE created_at < ?
        )
    """, (cutoff_str,))

    # Delete from incident_tickets
    cursor.execute("""
        DELETE FROM incident_tickets WHERE created_at < ?
    """, (cutoff_str,))

    conn.commit()
    conn.close()

# Run one cycle of execution
def run_once():
    initialize_database()
    insert_incident_data()
    rotate_data()

# Execute once for now
run_once()


#How to run for every 5 mins
#crontab -e
#*/5 * * * * /usr/bin/python3 /path/to/incident_logger.py
