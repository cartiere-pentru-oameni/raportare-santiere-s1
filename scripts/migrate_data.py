#!/usr/bin/env python3
"""Migrate data from Supabase to PostgreSQL"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg
from psycopg.types.json import Jsonb
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Connect to Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Connect to PostgreSQL
pg_conn = psycopg.connect(os.getenv('DATABASE_URL'))

# Tables to migrate in order (respecting foreign key constraints)
TABLES = [
    'official_users',
    'reports',
    'pictures',
    'comments',
    'reports_history',
    'permits',
    'permits_metadata',
    'contact_messages'
]

def migrate_table(table_name):
    """Migrate a single table from Supabase to PostgreSQL"""
    print(f"\n📦 Migrating {table_name}...")

    try:
        # Fetch all data from Supabase
        response = supabase.table(table_name).select('*').execute()
        data = response.data

        if not data:
            print(f"   ⚠️  No data found in {table_name}")
            return 0

        print(f"   Found {len(data)} rows")

        # Insert into PostgreSQL
        with pg_conn.cursor() as cur:
            for row in data:
                columns = list(row.keys())
                values = []

                # Convert dict values to Jsonb for JSONB columns
                for col in columns:
                    val = row[col]
                    if isinstance(val, dict):
                        values.append(Jsonb(val))
                    else:
                        values.append(val)

                placeholders = ','.join(['%s'] * len(columns))

                query = f"""
                    INSERT INTO {table_name} ({','.join(columns)})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """

                cur.execute(query, values)

        pg_conn.commit()
        print(f"   ✅ Migrated {len(data)} rows")
        return len(data)

    except Exception as e:
        print(f"   ❌ Error migrating {table_name}: {e}")
        pg_conn.rollback()
        return 0


def check_supabase_data():
    """Check what data exists in Supabase"""
    print("\n🔍 Checking Supabase data...")
    print("-" * 50)

    total = 0
    for table in TABLES:
        try:
            response = supabase.table(table).select('*', count='exact').execute()
            count = len(response.data)
            total += count
            print(f"   {table:20} {count:>6} rows")
        except Exception as e:
            print(f"   {table:20} ERROR: {e}")

    print("-" * 50)
    print(f"   {'TOTAL':20} {total:>6} rows")
    return total


def check_postgres_data():
    """Check what data exists in PostgreSQL"""
    print("\n🔍 Checking PostgreSQL data...")
    print("-" * 50)

    total = 0
    with pg_conn.cursor() as cur:
        for table in TABLES:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                total += count
                print(f"   {table:20} {count:>6} rows")
            except Exception as e:
                print(f"   {table:20} ERROR: {e}")

    print("-" * 50)
    print(f"   {'TOTAL':20} {total:>6} rows")
    return total


def main():
    print("=" * 50)
    print("DATA MIGRATION: Supabase → PostgreSQL")
    print("=" * 50)

    # Check source data
    supabase_total = check_supabase_data()

    if supabase_total == 0:
        print("\n⚠️  No data found in Supabase. Nothing to migrate.")
        return

    # Check destination data
    pg_total = check_postgres_data()

    # Confirm migration
    print("\n⚠️  WARNING: This will copy all data from Supabase to PostgreSQL")
    if pg_total > 0:
        print(f"   PostgreSQL already has {pg_total} rows. Duplicates will be skipped.")

    # Check for --yes flag
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv

    if not auto_confirm:
        confirm = input("\n❓ Proceed with migration? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("\n❌ Migration cancelled")
            return
    else:
        print("\n✅ Auto-confirmed (--yes flag)")

    # Perform migration
    print("\n🚀 Starting migration...")
    print("=" * 50)

    start_time = datetime.now()
    total_migrated = 0

    for table in TABLES:
        count = migrate_table(table)
        total_migrated += count

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Final check
    print("\n" + "=" * 50)
    print("MIGRATION COMPLETE")
    print("=" * 50)
    print(f"   Migrated: {total_migrated} rows")
    print(f"   Duration: {duration:.2f} seconds")

    check_postgres_data()

    pg_conn.close()
    print("\n✅ Done!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        pg_conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        pg_conn.close()
        sys.exit(1)
