# 部署指南

本文档详细说明如何部署软件秘钥授权系统。

## 部署选项

### 1. Render 部署（推荐）

Render 提供免费的 Python 应用托管服务。

#### 步骤：

1. **创建 Render 账户**
   - 访问 [render.com](https://render.com)
   - 注册账户并验证邮箱

2. **创建数据库**
   - 在 Render Dashboard 中创建 PostgreSQL 数据库
   - 记录数据库连接字符串

3. **部署应用**
   - 连接 GitHub 仓库
   - 选择 `deploy/render.yaml` 配置文件
   - 设置环境变量：
     ```
     DATABASE_URL=postgresql://username:password@host:port/database
     SECRET_KEY=your-secret-key-here
     ```

4. **配置域名**
   - 在应用设置中配置自定义域名（可选）

### 2. Railway 部署

Railway 提供简单的一键部署。

#### 步骤：

1. **创建 Railway 账户**
   - 访问 [railway.app](https://railway.app)
   - 使用 GitHub 登录

2. **部署应用**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择您的仓库

3. **配置环境变量**
   - 在项目设置中添加环境变量
   - 创建 PostgreSQL 数据库服务

4. **设置数据库**
   - 在 Railway 中创建 PostgreSQL 服务
   - 复制连接字符串到环境变量

### 3. Docker 部署

使用 Docker 进行本地或服务器部署。

#### 本地部署：

```bash
# 克隆项目
git clone <your-repo-url>
cd license-authorization-system

# 设置环境变量
cp env.example .env
# 编辑 .env 文件，设置数据库连接

# 启动服务
docker-compose up -d
```

#### 服务器部署：

```bash
# 在服务器上
git clone <your-repo-url>
cd license-authorization-system

# 设置环境变量
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your-secret-key"

# 构建并启动
docker-compose up -d
```

## 环境变量配置

### 必需变量：

- `DATABASE_URL`: PostgreSQL 数据库连接字符串
- `SECRET_KEY`: 用于加密的密钥（建议使用随机字符串）

### 可选变量：

- `DEBUG`: 调试模式（默认: False）
- `HOST`: 绑定主机（默认: 0.0.0.0）
- `PORT`: 绑定端口（默认: 8000）

## 数据库设置

### Supabase 设置：

1. **创建项目**
   - 访问 [supabase.com](https://supabase.com)
   - 创建新项目

2. **执行 SQL**
   - 在 SQL Editor 中执行 `database/schema.sql`
   - 创建必要的表和索引

3. **获取连接字符串**
   - 在 Settings > Database 中找到连接字符串
   - 格式：`postgresql://postgres:[password]@[host]:5432/postgres`

### 本地 PostgreSQL：

```bash
# 安装 PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb license_system

# 执行 SQL
sudo -u postgres psql license_system < database/schema.sql
```

## 安全配置

### 1. HTTPS 配置

- 使用 Let's Encrypt 免费 SSL 证书
- 配置反向代理（Nginx）
- 强制 HTTPS 重定向

### 2. 防火墙设置

```bash
# 只允许必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. 数据库安全

- 使用强密码
- 限制数据库访问 IP
- 定期备份数据

## 监控和日志

### 1. 应用监控

- 使用 Render/Railway 内置监控
- 配置健康检查端点
- 设置告警通知

### 2. 日志管理

```python
# 在 main.py 中配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 备份策略

### 1. 数据库备份

```bash
# 每日备份
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# 自动备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > "backup_${DATE}.sql"
gzip "backup_${DATE}.sql"
```

### 2. 配置备份

- 备份环境变量配置
- 备份 SSL 证书
- 备份应用配置文件

## 故障排除

### 常见问题：

1. **数据库连接失败**
   - 检查 DATABASE_URL 格式
   - 确认数据库服务运行状态
   - 检查网络连接

2. **应用启动失败**
   - 检查环境变量设置
   - 查看应用日志
   - 确认端口未被占用

3. **授权验证失败**
   - 检查数据库表结构
   - 验证授权码格式
   - 查看 API 日志

### 日志查看：

```bash
# Docker 日志
docker-compose logs -f

# Render 日志
# 在 Render Dashboard 中查看

# Railway 日志
# 在 Railway Dashboard 中查看
```

## 性能优化

### 1. 数据库优化

- 创建适当的索引
- 定期清理过期数据
- 使用连接池

### 2. 应用优化

- 启用 Gzip 压缩
- 使用 CDN 加速
- 配置缓存策略

### 3. 监控指标

- 响应时间
- 错误率
- 数据库连接数
- 内存使用率

## 更新和维护

### 1. 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新部署
docker-compose up -d --build
```

### 2. 数据库迁移

- 备份现有数据
- 执行新的 SQL 脚本
- 验证数据完整性

### 3. 安全更新

- 定期更新依赖包
- 监控安全漏洞
- 及时应用安全补丁
