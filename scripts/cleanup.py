#!/usr/bin/env python3
"""
Cleanup script to delete all reports and associated data from database and storage.
USE WITH CAUTION - THIS WILL DELETE ALL DATA!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables
load_dotenv()

# Import storage client
from app.storage import storage

# Connect to PostgreSQL
pg_conn = psycopg.connect(os.getenv('DATABASE_URL'))

def cleanup():
    print("⚠️  WARNING: This will delete ALL reports, pictures, and comments!")
    confirm = input("Type 'DELETE ALL' to confirm: ")

    if confirm != "DELETE ALL":
        print("Cancelled.")
        pg_conn.close()
        return

    print("\n🗑️  Deleting all data...")

    # Get all picture storage paths before deleting
    print("- Fetching picture storage paths...")
    with pg_conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT storage_path FROM pictures")
        pictures = cur.fetchall()

    # Delete all pictures from S3 storage
    print(f"- Deleting {len(pictures)} files from S3 storage...")
    deleted_count = 0
    for pic in pictures:
        try:
            storage.delete(pic['storage_path'])
            deleted_count += 1
            print(f"  Deleted: {pic['storage_path']}")
        except Exception as e:
            print(f"  Error deleting {pic['storage_path']}: {e}")
    print(f"  ✓ Deleted {deleted_count}/{len(pictures)} files from storage")

    # Delete all comments
    print("- Deleting comments...")
    try:
        with pg_conn.cursor() as cur:
            cur.execute("DELETE FROM comments")
            count = cur.rowcount
            pg_conn.commit()
        print(f"  ✓ Deleted {count} comments")
    except Exception as e:
        print(f"  Error: {e}")
        pg_conn.rollback()

    # Delete all pictures records
    print("- Deleting picture records...")
    try:
        with pg_conn.cursor() as cur:
            cur.execute("DELETE FROM pictures")
            count = cur.rowcount
            pg_conn.commit()
        print(f"  ✓ Deleted {count} picture records")
    except Exception as e:
        print(f"  Error: {e}")
        pg_conn.rollback()

    # Delete all reports
    print("- Deleting reports...")
    try:
        with pg_conn.cursor() as cur:
            cur.execute("DELETE FROM reports")
            count = cur.rowcount
            pg_conn.commit()
        print(f"  ✓ Deleted {count} reports")
    except Exception as e:
        print(f"  Error: {e}")
        pg_conn.rollback()

    # Delete all reports_history
    print("- Deleting reports history...")
    try:
        with pg_conn.cursor() as cur:
            cur.execute("DELETE FROM reports_history")
            count = cur.rowcount
            pg_conn.commit()
        print(f"  ✓ Deleted {count} history records")
    except Exception as e:
        print(f"  Error: {e}")
        pg_conn.rollback()

    pg_conn.close()
    print("\n✅ Cleanup complete!")

if __name__ == '__main__':
    try:
        cleanup()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        pg_conn.close()
        sys.exit(1)
