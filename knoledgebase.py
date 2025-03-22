#This is one time execution

import sqlite3
import random
from datetime import datetime

# Define database path
DB_PATH = "/mnt/data/knowledge_base.db"

# Sample applications and servers for CI simulation
applications = [f"App{i+1}" for i in range(5)]
servers = [f"Server{i+1}" for i in range(50)]

# Error categories and troubleshooting content
kb_articles = [
    {
        "title": "Database Connection Issues",
        "steps": "1. Check database service status.\n2. Verify connection strings.\n3. Restart DB services if needed.",
        "playbook": "Automated script to restart DB service and run health checks.",
        "rca_summary": "Frequent DB disconnects due to misconfigured firewall rules.",
        "patterns": "Recurring during peak traffic, usually after config changes."
    },
    {
        "title": "High CPU Usage on Servers",
        "steps": "1. Identify high CPU processes.\n2. Restart services consuming excess CPU.\n3. Optimize code.",
        "playbook": "Script to kill zombie processes and restart apps.",
        "rca_summary": "Memory leak in application caused CPU spike.",
        "patterns": "Observed post-deployment of version X.Y.Z."
    },
    {
        "title": "Network Latency Problems",
        "steps": "1. Run traceroute.\n2. Check switch/router health.\n3. Test alternate network paths.",
        "playbook": "Network diagnostics tool for packet loss and latency checks.",
        "rca_summary": "Faulty NIC card caused intermittent drops.",
        "patterns": "Specific to east-zone data center connections."
    },
    {
        "title": "UI Load Failures",
        "steps": "1. Check browser console for JS errors.\n2. Inspect API response errors.\n3. Clear cache and reload.",
        "playbook": "Frontend debugger to test API/UI loading behavior.",
        "rca_summary": "Angular version mismatch with backend API structure.",
        "patterns": "Happens after frontend-only deployments."
    },
    {
        "title": "API Timeout Errors",
        "steps": "1. Review request payload size.\n2. Analyze response time metrics.\n3. Optimize backend logic.",
        "playbook": "Tool to log and alert on slow API responses.",
        "rca_summary": "Unindexed DB queries caused backend slowdown.",
        "patterns": "Occurs during reporting operations."
    }
]

# Sample CI configuration details
network_topology = "Layered network with core, distribution, and access switches connected to servers via VLANs."
software_config = "Apps deployed via containers using Docker and Kubernetes. CI/CD enabled through Jenkins."
hardware_config = "All servers are 16-core machines with 64GB RAM and 1TB SSDs, running Linux."

# Create and populate the knowledge base
def create_knowledge_base():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create KB articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            troubleshooting_steps TEXT,
            playbook TEXT,
            rca_summary TEXT,
            failure_patterns TEXT
        )
    """)

    # Create configuration item (CI) data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuration_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application TEXT,
            server TEXT,
            network_topology TEXT,
            software_config TEXT,
            hardware_config TEXT
        )
    """)

    # Insert KB articles
    for article in kb_articles:
        cursor.execute("""
            INSERT INTO kb_articles (title, troubleshooting_steps, playbook, rca_summary, failure_patterns)
            VALUES (?, ?, ?, ?, ?)
        """, (
            article["title"],
            article["steps"],
            article["playbook"],
            article["rca_summary"],
            article["patterns"]
        ))

    # Insert CI data for each application and a few servers
    for app in applications:
        for server in random.sample(servers, 3):  # associate 3 servers per app
            cursor.execute("""
                INSERT INTO configuration_items (application, server, network_topology, software_config, hardware_config)
                VALUES (?, ?, ?, ?, ?)
            """, (
                app,
                server,
                network_topology,
                software_config,
                hardware_config
            ))

    conn.commit()
    conn.close()

# Run once
create_knowledge_base()

DB_PATH
