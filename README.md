# 软件秘钥授权系统

一个完整的软件授权管理系统，支持多种授权类型和在线验证。

## 功能特性

- 支持多种授权类型：1天试用、3天试用、30天、180天、365天、永久使用权
- 在线授权码验证
- 安全的授权码生成
- 支持用户邮箱绑定
- 完整的API接口
- 客户端示例代码

## 系统架构

- **后端**: FastAPI (Python)
- **数据库**: Supabase (PostgreSQL)
- **部署**: Render/Railway
- **客户端**: 支持多种语言 (Python, C#, Java等)

## 快速开始

### 1. 数据库设置

在Supabase中创建项目并执行以下SQL创建表：

```sql
-- 创建licenses表
CREATE TABLE licenses (
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

-- 创建索引
CREATE INDEX idx_license_key ON licenses(license_key);
CREATE INDEX idx_user_email ON licenses(user_email);
CREATE INDEX idx_plan_type ON licenses(plan_type);
```

### 2. 后端部署

1. 克隆项目到Render/Railway
2. 设置环境变量：
   - `DATABASE_URL`: Supabase数据库连接字符串
   - `SECRET_KEY`: 用于JWT签名的密钥
3. 部署应用

### 3. 客户端集成

参考 `client_examples/` 目录中的示例代码集成到您的软件中。

## API文档

### 验证授权码
```
GET /verify/{license_key}
```

### 生成授权码（管理端）
```
POST /generate
Content-Type: application/json

{
    "plan_type": "30d",
    "user_email": "user@example.com"
}
```

## 安全特性

- HTTPS通信
- 随机授权码生成
- 数据库权限控制
- 请求日志记录
- 输入验证和清理

## 许可证

MIT License
