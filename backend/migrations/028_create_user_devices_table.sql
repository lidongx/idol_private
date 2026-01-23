-- Migration 028: Create user_devices table
-- Story 8.1: 多设备登录与设备管理
-- Date: 2026-01-19
-- Description: Track user login devices for multi-device sync (max 5 devices per user)

-- Create user_devices table
CREATE TABLE IF NOT EXISTS user_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    device_model VARCHAR(100) NULL,
    os_version VARCHAR(50) NULL,
    app_version VARCHAR(50) NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_ip_address VARCHAR(45) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_user_devices_user_id ON user_devices(user_id);
CREATE INDEX idx_user_devices_device_id ON user_devices(device_id);
CREATE INDEX idx_user_devices_last_login ON user_devices(last_login_at DESC);
CREATE UNIQUE INDEX idx_user_devices_user_device ON user_devices(user_id, device_id);

-- Add comments
COMMENT ON TABLE user_devices IS '用户设备管理表';
COMMENT ON COLUMN user_devices.user_id IS '用户ID';
COMMENT ON COLUMN user_devices.device_id IS '设备唯一标识符（UUID）';
COMMENT ON COLUMN user_devices.device_name IS '用户友好的设备名称';
COMMENT ON COLUMN user_devices.device_type IS '设备类型: ios, android, web';
COMMENT ON COLUMN user_devices.device_model IS '设备型号（如：iPhone 15 Pro）';
COMMENT ON COLUMN user_devices.os_version IS '操作系统版本（如：iOS 17.2）';
COMMENT ON COLUMN user_devices.app_version IS '应用版本';
COMMENT ON COLUMN user_devices.is_active IS '设备是否激活';
COMMENT ON COLUMN user_devices.last_login_at IS '最后登录时间';
COMMENT ON COLUMN user_devices.last_ip_address IS '最后登录IP地址（IPv4或IPv6）';
COMMENT ON COLUMN user_devices.created_at IS '创建时间';
COMMENT ON COLUMN user_devices.updated_at IS '更新时间';
