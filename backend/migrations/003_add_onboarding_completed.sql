-- Add onboarding_completed field to users table
-- Migration: 003_add_onboarding_completed
-- Description: Track whether user has completed onboarding flow

ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false;

-- Update existing users to have onboarding_completed = false
UPDATE users SET onboarding_completed = false WHERE onboarding_completed IS NULL;

-- Create index for efficient querying
CREATE INDEX IF NOT EXISTS idx_users_onboarding ON users(onboarding_completed);
