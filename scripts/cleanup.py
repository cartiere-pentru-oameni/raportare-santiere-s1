#!/usr/bin/env python3
"""
Cleanup script to delete all reports and associated data from database and storage.
USE WITH CAUTION - THIS WILL DELETE ALL DATA!
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client with service role (full access)
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

def cleanup():
    print("⚠️  WARNING: This will delete ALL reports, pictures, and comments!")
    confirm = input("Type 'DELETE ALL' to confirm: ")

    if confirm != "DELETE ALL":
        print("Cancelled.")
        return

    print("\n🗑️  Deleting all data...")

    # Delete all pictures from storage
    print("- Deleting storage files...")
    try:
        # List all files in bucket
        files = supabase.storage.from_('report-pictures').list()

        # Delete all folders/files
        for item in files:
            if item.get('name'):
                try:
                    supabase.storage.from_('report-pictures').remove([item['name']])
                    print(f"  Deleted: {item['name']}")
                except Exception as e:
                    print(f"  Error deleting {item['name']}: {e}")
    except Exception as e:
        print(f"  Storage cleanup error: {e}")

    # Delete all comments
    print("- Deleting comments...")
    try:
        supabase.table('comments').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("  ✓ Comments deleted")
    except Exception as e:
        print(f"  Error: {e}")

    # Delete all pictures records
    print("- Deleting picture records...")
    try:
        supabase.table('pictures').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("  ✓ Picture records deleted")
    except Exception as e:
        print(f"  Error: {e}")

    # Delete all reports
    print("- Deleting reports...")
    try:
        supabase.table('reports').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("  ✓ Reports deleted")
    except Exception as e:
        print(f"  Error: {e}")

    # Delete all reports_history
    print("- Deleting reports history...")
    try:
        supabase.table('reports_history').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("  ✓ Reports history deleted")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n✅ Cleanup complete!")

if __name__ == '__main__':
    cleanup()
