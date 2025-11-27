-- Clean up old migration artifacts
-- Run this to fix the duplicate enum error

-- Drop old enum types from previous migration
DROP TYPE IF EXISTS file_format CASCADE;
DROP TYPE IF EXISTS ingestion_status CASCADE;

-- Check what enum types exist
SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname;
