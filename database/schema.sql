-- 软件秘钥授权系统数据库表结构
-- 适用于 Supabase PostgreSQL

-- 创建licenses表
CREATE TABLE IF NOT EXISTS licenses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    license_key TEXT UNIQUE NOT NULL,
    user_email TEXT,
    plan_type TEXT NOT NULL CHECK (plan_type IN ('trial1', 'trial3', '30d', '180d', '365d', 'lifetime')),
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key);
CREATE INDEX IF NOT EXISTS idx_user_email ON licenses(user_email);
CREATE INDEX IF NOT EXISTS idx_plan_type ON licenses(plan_type);
CREATE INDEX IF NOT EXISTS idx_is_active ON licenses(is_active);
CREATE INDEX IF NOT EXISTS idx_end_date ON licenses(end_date);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_licenses_updated_at 
    BEFORE UPDATE ON licenses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 插入示例数据（可选）
INSERT INTO licenses (license_key, user_email, plan_type, end_date) VALUES
('DEMO-TRIAL1-ABCD1234', 'demo@example.com', 'trial1', NOW() + INTERVAL '1 day'),
('DEMO-TRIAL3-EFGH5678', 'demo@example.com', 'trial3', NOW() + INTERVAL '3 days'),
('DEMO-30D-IJKL9012', 'demo@example.com', '30d', NOW() + INTERVAL '30 days'),
('DEMO-LIFETIME-MNOP3456', 'demo@example.com', 'lifetime', NULL)
ON CONFLICT (license_key) DO NOTHING;
