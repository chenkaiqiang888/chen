# Render 部署指南

## 🚀 使用Render部署在线授权系统

本指南将帮助您使用Render免费平台部署软件秘钥授权系统。

### 📋 部署前准备

**1. 注册Render账号**
- 访问 [render.com](https://render.com)
- 使用GitHub账号注册（推荐）

**2. 准备GitHub仓库**
- 将项目代码推送到GitHub
- 确保包含所有必要文件

### 🔧 部署步骤

#### 第一步：创建PostgreSQL数据库

1. **登录Render控制台**
2. **创建新服务**
   - 点击 "New +"
   - 选择 "PostgreSQL"

3. **配置数据库**
   ```
   Name: license-db
   Database: license_system
   User: license_user
   Region: 选择离您最近的区域
   Plan: Free
   ```

4. **获取数据库连接信息**
   - 记录 `External Database URL`
   - 格式：`postgresql://user:password@host:port/database`

#### 第二步：部署Web服务

1. **创建Web服务**
   - 点击 "New +"
   - 选择 "Web Service"

2. **连接GitHub仓库**
   - 选择您的项目仓库
   - 选择主分支

3. **配置服务**
   ```
   Name: license-authorization-system
   Environment: Python 3
   Region: 选择与数据库相同的区域
   Branch: main
   Root Directory: (留空)
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **设置环境变量**
   ```
   DATABASE_URL: postgresql://user:password@host:port/database
   SECRET_KEY: (自动生成)
   APP_NAME: License Authorization System
   DEBUG: False
   HOST: 0.0.0.0
   PORT: 8000
   ```

#### 第三步：自动部署

1. **保存配置**
   - 点击 "Create Web Service"
   - Render将自动开始部署

2. **等待部署完成**
   - 构建过程需要几分钟
   - 查看部署日志确认成功

3. **获取服务URL**
   - 部署完成后获得HTTPS URL
   - 格式：`https://your-app-name.onrender.com`

### 🔍 验证部署

**1. 健康检查**
```bash
curl https://your-app-name.onrender.com/health
```

**2. API文档**
```bash
访问: https://your-app-name.onrender.com/docs
```

**3. 测试授权码生成**
```bash
curl -X POST "https://your-app-name.onrender.com/generate" \
     -H "Content-Type: application/json" \
     -d '{"user_email": "test@example.com", "plan_type": "30d"}'
```

### 📱 客户端软件配置

**修改客户端API地址：**
```python
# license_client.py
class LicenseClient:
    def __init__(self, api_base_url="https://your-app-name.onrender.com"):
        self.api_base_url = api_base_url
```

### 🛠️ 管理功能

**1. 查看服务状态**
- 登录Render控制台
- 查看服务运行状态和日志

**2. 重启服务**
- 在服务页面点击 "Manual Deploy"
- 选择 "Deploy latest commit"

**3. 查看日志**
- 点击 "Logs" 标签
- 实时查看应用日志

### 💰 费用说明

**免费套餐限制：**
- **Web服务**: 750小时/月
- **PostgreSQL**: 1GB存储
- **带宽**: 100GB/月
- **自动休眠**: 15分钟无活动后休眠

**实际使用：**
- 750小时 = 31.25天
- 基本可以24小时运行
- 休眠后首次访问需要几秒唤醒

### 🔒 安全配置

**1. 环境变量安全**
- 不要将敏感信息提交到代码
- 使用Render的环境变量功能

**2. HTTPS**
- Render自动提供HTTPS
- 所有通信都经过加密

**3. 数据库安全**
- 数据库仅限Render内部访问
- 外部无法直接连接

### 🚨 故障排除

**常见问题：**

1. **部署失败**
   - 检查requirements.txt
   - 确认Python版本兼容性
   - 查看构建日志

2. **数据库连接失败**
   - 确认DATABASE_URL正确
   - 检查数据库服务状态
   - 验证网络连接

3. **服务无法访问**
   - 检查服务状态
   - 确认端口配置
   - 查看应用日志

### 📞 技术支持

**Render支持：**
- 官方文档：https://render.com/docs
- 社区论坛：https://community.render.com
- 邮件支持：support@render.com

**项目支持：**
- 查看项目README
- 检查部署日志
- 验证环境变量配置

### 🎉 部署完成

部署成功后，您将获得：
- ✅ 在线授权验证API
- ✅ 实时授权码管理
- ✅ 全球可访问的HTTPS服务
- ✅ 自动备份的PostgreSQL数据库
- ✅ 完整的Web管理界面

**您的在线授权系统现在已经可以使用了！** 🚀
