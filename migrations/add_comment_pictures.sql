-- Migration: Add comment pictures support
-- Created: 2026-02-15
-- Description: Adds comment_pictures table and updated_at column to comments table

-- Create comment_pictures table
CREATE TABLE IF NOT EXISTS comment_pictures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_comment_pictures_comment_id ON comment_pictures(comment_id);

-- Add updated_at column to comments table for edit tracking
ALTER TABLE comments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;
