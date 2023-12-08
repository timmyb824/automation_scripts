##################################################################
## Replicate Postgres databases from one RDS instance to another##
## Author: Timothy Bryant                                       ##
##################################################################
import os
import subprocess

import psycopg2

# Source RDS instance connection details
source_host = os.environ.get("SOURCE_HOST")
source_port = "5432"
source_user = os.environ.get("SOURCE_USER")
source_password = os.environ.get("SOURCE_PASSWORD")
source_db = "postgres"

# Destination RDS instance connection details
dest_host = os.environ.get("DEST_HOST")
dest_port = "5432"
dest_user = os.environ.get("DEST_USER")
dest_password = os.environ.get("DEST_PASSWORD")
dest_db = "postgres"

# Connect to source database
print("Connecting to source database...\n")
source_conn = psycopg2.connect(
    host=source_host,
    port=source_port,
    database=source_db,
    user=source_user,
    password=source_password,
)

# Get list of all databases on the source RDS instance
print("Getting list of databases...\n")
source_cursor = source_conn.cursor()
source_cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
databases = source_cursor.fetchall()

# Loop through all databases
for database in databases:
    database_name = database[0]

    # Skip 'postgres' and 'rdsadmin' system databases
    if database_name in ["postgres", "rdsadmin"]:
        continue

    print(f"Dumping database: {database_name}")

    source_env = os.environ.copy()
    source_env["PGPASSWORD"] = source_password
    # Dump the database to a file using pg_dump
    subprocess.call(
        [
            "pg_dump",
            "-h",
            source_host,
            "-p",
            source_port,
            "-U",
            source_user,
            "-w",
            "-F",
            "c",
            "-b",
            "-v",
            "-f",
            f"./backups/{database_name}.dump",
            database_name,
        ],
        env=source_env,
    )

    # Connect to destination database
    print("\nConnecting to destination database...\n")
    dest_conn = psycopg2.connect(
        host=dest_host,
        port=dest_port,
        database=dest_db,
        user=dest_user,
        password=dest_password,
    )

    dest_conn.autocommit = True

    # Restore the database dump into the destination RDS instance
    print(f"Restoring database: {database_name}\n")
    dest_cursor = dest_conn.cursor()
    # Terminate all connections to the database else the restore will fail
    dest_cursor.execute(
        f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database_name}' AND pid <> pg_backend_pid();"
    )
    # Use "" to escape the database name
    dest_cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
    dest_cursor.execute(f'CREATE DATABASE "{database_name}"')
    dest_env = os.environ.copy()
    dest_env["PGPASSWORD"] = dest_password
    subprocess.call(
        [
            "pg_restore",
            "-h",
            dest_host,
            "-p",
            dest_port,
            "-U",
            dest_user,
            "-w",
            "-c",
            "-v",
            "-d",
            database_name,
            f"./backups/{database_name}.dump",
        ],
        env=dest_env,
    )
    dest_conn.commit()
    print(f"Database restored: {database_name}\n")

    # Close the connection
    dest_cursor.close()
    dest_conn.close()

source_cursor.close()
source_conn.close()
print("Connection closed: source")
