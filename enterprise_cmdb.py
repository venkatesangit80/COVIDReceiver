import sqlite3
import random
from datetime import datetime

# Define database path
DB_PATH = "/mnt/data/enterprise_cmdb.db"

# Sample applications and services
applications = [f"App{i+1}" for i in range(5)]
services = ["AuthService", "PaymentService", "NotificationService", "UserProfileService", "ReportingService"]
environments = ["Production", "Staging", "Development"]
servers = [f"Server{i+1}" for i in range(50)]
vendors = ["AWS", "Azure", "GCP", "On-Prem"]

# Create and populate the Enterprise CMDB and MCP integration logs
def create_enterprise_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create CMDB table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cmdb (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application TEXT,
            environment TEXT,
            service_dependency TEXT,
            architecture_details TEXT,
            server TEXT,
            asset_tag TEXT,
            vendor TEXT,
            created_at TEXT
        )
    """)

    # Create MCP data log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application TEXT,
            system_name TEXT,
            log_type TEXT,
            api_name TEXT,
            response_code INTEGER,
            response_time_ms REAL,
            timestamp TEXT
        )
    """)

    # Insert CMDB data
    for app in applications:
        for _ in range(3):  # 3 entries per app
            env = random.choice(environments)
            dependency = random.choice(services)
            architecture = f"{app} uses microservices with {dependency} and external APIs"
            server = random.choice(servers)
            asset_tag = f"AT-{random.randint(10000,99999)}"
            vendor = random.choice(vendors)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO cmdb (application, environment, service_dependency, architecture_details, server, asset_tag, vendor, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (app, env, dependency, architecture, server, asset_tag, vendor, created_at))

    # Insert MCP logs
    api_endpoints = ["/auth/login", "/payment/process", "/notify/send", "/user/profile", "/report/generate"]
    for _ in range(30):  # 30 sample logs
        app = random.choice(applications)
        system = random.choice(["CRM", "ERP", "BillingSystem", "AnalyticsEngine"])
        log_type = random.choice(["INFO", "ERROR", "WARN", "DEBUG"])
        api = random.choice(api_endpoints)
        response_code = random.choice([200, 201, 400, 401, 403, 500])
        response_time = round(random.uniform(50, 1000), 2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO mcp_logs (application, system_name, log_type, api_name, response_code, response_time_ms, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (app, system, log_type, api, response_code, response_time, timestamp))

    conn.commit()
    conn.close()

# Run one-time population
create_enterprise_data()

DB_PATH
