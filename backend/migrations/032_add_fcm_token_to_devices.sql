-- Migration 032: Add FCM Token to User Devices
-- Story 9.3: 推送通知集成（Firebase Cloud Messaging）
-- Created: 2026-01-19
--
-- Purpose: Add FCM token field to user_devices table for push notifications

-- Add fcm_token column to user_devices table
ALTER TABLE user_devices
ADD COLUMN fcm_token VARCHAR(255) NULL;

-- Add index for faster FCM token lookups
CREATE INDEX idx_user_devices_fcm_token ON user_devices(fcm_token);

-- Add comment
COMMENT ON COLUMN user_devices.fcm_token IS 'Firebase Cloud Messaging device token for push notifications';

COMMIT;
