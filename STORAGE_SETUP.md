# Supabase Storage Setup

## Create Bucket

1. Go to Supabase Dashboard → Storage
2. Create new bucket: `report-pictures`
3. **Important:** Set bucket to **PRIVATE** (not public)

## Add RLS Policies to Bucket

Run this SQL in Supabase SQL Editor:

```sql
-- Allow authenticated service role (validators/admins) to upload
CREATE POLICY "Service role can upload" ON storage.objects
FOR INSERT TO service_role
WITH CHECK (bucket_id = 'report-pictures');

-- Allow authenticated service role to delete
CREATE POLICY "Service role can delete" ON storage.objects
FOR DELETE TO service_role
USING (bucket_id = 'report-pictures');

-- Allow anon users to upload (citizens submitting reports)
CREATE POLICY "Anon can upload" ON storage.objects
FOR INSERT TO anon
WITH CHECK (bucket_id = 'report-pictures');

-- Public can view pictures only for reports with status in-review, validated, or resolved
CREATE POLICY "Public can view approved pictures" ON storage.objects
FOR SELECT
USING (
  bucket_id = 'report-pictures'
  AND EXISTS (
    SELECT 1 FROM pictures
    JOIN reports ON reports.id = pictures.report_id
    WHERE pictures.storage_path = storage.objects.name
    AND reports.status IN ('in-review', 'validated', 'resolved')
  )
);
```

## File Restrictions

- **Max files per report:** 10
- **Max file size:** 10MB
- **Allowed types:** image/jpeg, image/png, image/webp
- **EXIF stripping:** Automatic on server side
