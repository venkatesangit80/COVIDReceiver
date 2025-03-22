import sqlite3
import os
import random
from datetime import datetime, timedelta

# List of applications and servers (same 5 apps and 50 servers as in related incident management script)
applications = [f"App{i+1}" for i in range(5)]
servers = [f"Server{i+1}" for i in range(50)]

# Define some sample error types and messages for simulation
error_types = [
    "DatabaseError",
    "NetworkError",
    "ApplicationException",
    "TimeoutError",
    "ValidationError"
]
error_messages = {
    "DatabaseError": "Database connection failed",
    "NetworkError": "Network unreachable",
    "ApplicationException": "Unexpected application error",
    "TimeoutError": "Operation timed out",
    "ValidationError": "Input validation failed"
}

def run_once():
    """Executes one cycle of data insertion and cleanup."""
    db_path = "/mnt/data/system_logs.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they do not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS real_time_monitoring (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            server TEXT,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            network_usage REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS application_error_logs (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            application TEXT,
            server TEXT,
            error_type TEXT,
            message TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_metrics (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            application TEXT,
            server TEXT,
            response_time REAL,
            latency REAL,
            failure_rate REAL
        )
    """)
    
    # Insert moderate randomized entries into each table
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    # real_time_monitoring: random server metrics entries
    for _ in range(random.randint(5, 10)):  # moderate number of entries
        server = random.choice(servers)
        cpu = random.uniform(1, 100)   # CPU usage percentage
        mem = random.uniform(1, 100)   # Memory usage percentage
        disk = random.uniform(1, 100)  # Disk usage percentage
        net = random.uniform(0, 1000)  # Network traffic (e.g., MB/s or similar unit)
        cursor.execute(
            "INSERT INTO real_time_monitoring (timestamp, server, cpu_usage, memory_usage, disk_usage, network_usage) VALUES (?, ?, ?, ?, ?, ?)",
            (now_str, server, round(cpu, 2), round(mem, 2), round(disk, 2), round(net, 2))
        )
    # application_error_logs: random error events
    for _ in range(random.randint(1, 5)):  # fewer error events typically
        app = random.choice(applications)
        server = random.choice(servers)
        err_type = random.choice(error_types)
        message = error_messages.get(err_type, "Unknown error occurred")
        cursor.execute(
            "INSERT INTO application_error_logs (timestamp, application, server, error_type, message) VALUES (?, ?, ?, ?, ?)",
            (now_str, app, server, err_type, message)
        )
    # telemetry_metrics: random telemetry readings
    for _ in range(random.randint(5, 10)):
        app = random.choice(applications)
        server = random.choice(servers)
        response_time = random.uniform(0, 1000)  # e.g., response time in ms
        latency = random.uniform(0, 500)         # e.g., network latency in ms
        failure_rate = random.uniform(0, 0.2)    # e.g., failure rate (0 to 0.2, representing 0-20%)
        cursor.execute(
            "INSERT INTO telemetry_metrics (timestamp, application, server, response_time, latency, failure_rate) VALUES (?, ?, ?, ?, ?, ?)",
            (now_str, app, server, round(response_time, 2), round(latency, 2), round(failure_rate, 4))
        )
    
    # Apply 5-hour retention policy: delete data older than 5 hours
    cutoff_time = datetime.now() - timedelta(hours=5)
    cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("DELETE FROM real_time_monitoring WHERE timestamp < ?", (cutoff_str,))
    cursor.execute("DELETE FROM application_error_logs WHERE timestamp < ?", (cutoff_str,))
    cursor.execute("DELETE FROM telemetry_metrics WHERE timestamp < ?", (cutoff_str,))
    
    # Commit changes and close
    conn.commit()
    conn.close()

# If this script is run directly, execute one cycle
if __name__ == "__main__":
    run_once()
