#!/usr/bin/env python3
"""Migrate images from Supabase Storage to Hetzner Object Storage (S3-compatible)"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
from botocore.exceptions import ClientError
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import psycopg
from psycopg.rows import dict_row

# Load environment variables
load_dotenv()

# Hetzner Object Storage configuration
HETZNER_ENDPOINT = 'https://fsn1.your-objectstorage.com'
HETZNER_BUCKET = 'cpo-private-autorizatii-upload-p8g91fl0'
HETZNER_ACCESS_KEY = 'KGKL0O3RJ3ZA58AVMP76'
HETZNER_SECRET_KEY = 'SEw31d21sCmYT0YkVOzEEWVYNKDemqhOVvRVFaAw'

# Connect to Supabase Storage
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Connect to Hetzner S3
s3_client = boto3.client(
    's3',
    endpoint_url=HETZNER_ENDPOINT,
    aws_access_key_id=HETZNER_ACCESS_KEY,
    aws_secret_access_key=HETZNER_SECRET_KEY,
    region_name='fsn1'  # Hetzner region
)

# Connect to PostgreSQL
pg_conn = psycopg.connect(os.getenv('DATABASE_URL'))


def test_s3_connection():
    """Test connection to Hetzner Object Storage"""
    print("\n🔍 Testing Hetzner S3 connection...")
    try:
        # Try to list buckets
        response = s3_client.list_buckets()
        print(f"   ✅ Connected! Found {len(response['Buckets'])} bucket(s)")

        # Check if our bucket exists
        buckets = [b['Name'] for b in response['Buckets']]
        if HETZNER_BUCKET in buckets:
            print(f"   ✅ Bucket '{HETZNER_BUCKET}' exists")
        else:
            print(f"   ⚠️  Bucket '{HETZNER_BUCKET}' not found")
            print(f"   Available buckets: {buckets}")

        return True
    except ClientError as e:
        print(f"   ❌ Connection failed: {e}")
        return False


def get_pictures_to_migrate():
    """Get all pictures from database"""
    print("\n📦 Fetching pictures from database...")

    with pg_conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, report_id, storage_path FROM pictures ORDER BY created_at")
        pictures = cur.fetchall()

    print(f"   Found {len(pictures)} picture(s) to migrate")
    return pictures


def migrate_picture(picture):
    """Migrate a single picture from Supabase to Hetzner"""
    storage_path = picture['storage_path']

    try:
        # Download from Supabase Storage
        response = supabase.storage.from_('report-pictures').download(storage_path)
        image_data = response

        if not image_data:
            print(f"   ⚠️  No data downloaded for {storage_path}")
            return False

        # Determine content type based on extension
        ext = storage_path.rsplit('.', 1)[1].lower() if '.' in storage_path else 'jpg'
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        content_type = content_type_map.get(ext, 'image/jpeg')

        # Upload to Hetzner S3
        s3_client.put_object(
            Bucket=HETZNER_BUCKET,
            Key=storage_path,
            Body=image_data,
            ContentType=content_type
        )

        print(f"   ✅ Migrated: {storage_path} ({len(image_data)} bytes)")
        return True

    except Exception as e:
        print(f"   ❌ Failed to migrate {storage_path}: {e}")
        return False


def verify_migration():
    """Verify all pictures are in Hetzner S3"""
    print("\n🔍 Verifying migration...")

    pictures = get_pictures_to_migrate()

    success = 0
    failed = []

    for picture in pictures:
        storage_path = picture['storage_path']
        try:
            # Check if object exists in S3
            s3_client.head_object(Bucket=HETZNER_BUCKET, Key=storage_path)
            success += 1
        except ClientError:
            failed.append(storage_path)

    print(f"\n   ✅ Verified: {success}/{len(pictures)} pictures")

    if failed:
        print(f"   ❌ Missing: {len(failed)} pictures")
        for path in failed:
            print(f"      - {path}")

    return len(failed) == 0


def main():
    print("=" * 70)
    print("STORAGE MIGRATION: Supabase → Hetzner Object Storage")
    print("=" * 70)

    # Test S3 connection first
    if not test_s3_connection():
        print("\n❌ Cannot connect to Hetzner S3. Please check credentials.")
        return

    # Get pictures to migrate
    pictures = get_pictures_to_migrate()

    if not pictures:
        print("\n⚠️  No pictures to migrate")
        return

    # Confirm migration
    print("\n⚠️  WARNING: This will copy all images to Hetzner Object Storage")
    print(f"   Source: Supabase Storage (report-pictures)")
    print(f"   Destination: {HETZNER_ENDPOINT}/{HETZNER_BUCKET}")

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
    print("=" * 70)

    start_time = datetime.now()
    success_count = 0
    failed_count = 0

    for i, picture in enumerate(pictures, 1):
        print(f"\n[{i}/{len(pictures)}]", end=" ")
        if migrate_picture(picture):
            success_count += 1
        else:
            failed_count += 1

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Verify migration
    verify_migration()

    # Summary
    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print(f"   Success: {success_count}/{len(pictures)}")
    print(f"   Failed: {failed_count}/{len(pictures)}")
    print(f"   Duration: {duration:.2f} seconds")

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
        import traceback
        traceback.print_exc()
        pg_conn.close()
        sys.exit(1)
