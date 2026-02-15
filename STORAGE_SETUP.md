# Hetzner Object Storage Setup

## Create Bucket

1. Log in to Hetzner Cloud Console
2. Navigate to Object Storage
3. Create new bucket with **PRIVATE** visibility
4. Note down the following credentials:
   - Endpoint URL (e.g., `https://fsn1.your-objectstorage.com`)
   - Bucket name
   - Access key
   - Secret key
   - Region (e.g., `fsn1`)

## Configure Application

Add the following to your `.env` file:

```env
# Hetzner Object Storage (S3-compatible)
S3_ENDPOINT=https://fsn1.your-objectstorage.com
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=fsn1
```

## Security Features

- **Private bucket:** All files require presigned URLs for access
- **Presigned URLs:** Generated server-side, valid for 1 hour
- **Access control:** Only reports with status `in-review`, `validated`, or `resolved` have accessible images
- **EXIF stripping:** Automatic on server side for privacy
- **No public access:** Direct file URLs will not work

## File Restrictions

- **Max files per report:** 10
- **Max file size:** 10MB
- **Allowed types:** image/jpeg, image/png, image/webp

## Storage Operations

The application uses boto3 (AWS S3 SDK) for all storage operations:
- Upload images with EXIF stripped
- Generate presigned URLs for temporary access
- Delete images when reports are removed
- Check file existence

## Migration from Supabase

If migrating from Supabase Storage, use the migration script:

```bash
python scripts/migrate_storage.py --yes
```

This will copy all existing images from Supabase to Hetzner Object Storage.
