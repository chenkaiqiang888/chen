# API 文档

软件秘钥授权系统的完整 API 文档。

## 基础信息

- **Base URL**: `https://your-api-server.com`
- **API Version**: v1
- **Content-Type**: `application/json`
- **Authentication**: 无需认证（公开 API）

## 响应格式

所有 API 响应都使用 JSON 格式：

```json
{
  "status": "success|error",
  "data": {},
  "message": "描述信息",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 错误响应

```json
{
  "error": true,
  "message": "错误描述",
  "status_code": 400,
  "error_code": "ERROR_CODE"
}
```

## 端点列表

### 1. 根路径

**GET** `/`

获取 API 基本信息。

#### 响应示例：

```json
{
  "message": "软件秘钥授权系统 API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "verify": "/verify/{license_key}",
    "generate": "/generate"
  }
}
```

### 2. 健康检查

**GET** `/health`

检查服务健康状态。

#### 响应示例：

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "database": "connected"
}
```

#### 错误响应：

```json
{
  "error": true,
  "message": "Service unavailable",
  "status_code": 503
}
```

### 3. 验证授权码

**GET** `/verify/{license_key}`

验证授权码的有效性。

#### 路径参数：

- `license_key` (string, required): 授权码

#### 响应示例：

**成功验证：**

```json
{
  "status": "valid",
  "plan_type": "30d",
  "end_date": "2024-02-01T00:00:00Z",
  "user_email": "user@example.com",
  "message": "授权码验证成功"
}
```

**授权码过期：**

```json
{
  "status": "expired",
  "plan_type": "30d",
  "end_date": "2024-01-01T00:00:00Z",
  "user_email": "user@example.com",
  "message": "授权码已过期"
}
```

**授权码被禁用：**

```json
{
  "status": "disabled",
  "message": "授权码已被禁用"
}
```

**授权码不存在：**

```json
{
  "status": "not_found",
  "message": "授权码不存在"
}
```

#### 状态码：

- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

### 4. 生成授权码

**POST** `/generate`

生成新的授权码（管理端接口）。

#### 请求体：

```json
{
  "plan_type": "30d",
  "user_email": "user@example.com"
}
```

#### 参数说明：

- `plan_type` (string, required): 授权类型
  - `trial1`: 1天试用
  - `trial3`: 3天试用
  - `30d`: 30天
  - `180d`: 180天
  - `365d`: 365天
  - `lifetime`: 永久使用权
- `user_email` (string, optional): 用户邮箱

#### 响应示例：

```json
{
  "license_key": "ABCD-1234-EFGH-5678",
  "plan_type": "30d",
  "end_date": "2024-02-01T00:00:00Z",
  "user_email": "user@example.com",
  "message": "成功生成30d授权码"
}
```

#### 状态码：

- `200`: 成功
- `400`: 请求参数错误
- `422`: 验证错误
- `500`: 服务器内部错误

## 授权类型说明

| 类型 | 描述 | 有效期 |
|------|------|--------|
| `trial1` | 1天试用 | 1天 |
| `trial3` | 3天试用 | 3天 |
| `30d` | 30天授权 | 30天 |
| `180d` | 180天授权 | 180天 |
| `365d` | 365天授权 | 365天 |
| `lifetime` | 永久使用权 | 无限制 |

## 授权码格式

授权码格式：`XXXX-XXXX-XXXX-XXXX`

- 每组4个字符
- 使用大写字母和数字
- 排除容易混淆的字符（0, O, I, L等）

示例：`ABCD-1234-EFGH-5678`

## 错误代码

| 错误代码 | 描述 |
|----------|------|
| `VALIDATION_ERROR` | 请求参数验证失败 |
| `LICENSE_NOT_FOUND` | 授权码不存在 |
| `LICENSE_EXPIRED` | 授权码已过期 |
| `LICENSE_DISABLED` | 授权码已被禁用 |
| `LICENSE_INVALID_FORMAT` | 授权码格式无效 |
| `DATABASE_ERROR` | 数据库操作失败 |
| `INTERNAL_SERVER_ERROR` | 服务器内部错误 |

## 使用示例

### Python 示例：

```python
import requests

# 验证授权码
def verify_license(license_key):
    url = f"https://your-api-server.com/verify/{license_key}"
    response = requests.get(url)
    return response.json()

# 生成授权码
def generate_license(plan_type, user_email=None):
    url = "https://your-api-server.com/generate"
    data = {
        "plan_type": plan_type,
        "user_email": user_email
    }
    response = requests.post(url, json=data)
    return response.json()

# 使用示例
result = verify_license("ABCD-1234-EFGH-5678")
if result["status"] == "valid":
    print("授权验证成功")
else:
    print(f"授权验证失败: {result['message']}")
```

### JavaScript 示例：

```javascript
// 验证授权码
async function verifyLicense(licenseKey) {
    const response = await fetch(`https://your-api-server.com/verify/${licenseKey}`);
    return await response.json();
}

// 生成授权码
async function generateLicense(planType, userEmail = null) {
    const response = await fetch('https://your-api-server.com/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            plan_type: planType,
            user_email: userEmail
        })
    });
    return await response.json();
}

// 使用示例
verifyLicense('ABCD-1234-EFGH-5678')
    .then(result => {
        if (result.status === 'valid') {
            console.log('授权验证成功');
        } else {
            console.log(`授权验证失败: ${result.message}`);
        }
    });
```

### cURL 示例：

```bash
# 验证授权码
curl -X GET "https://your-api-server.com/verify/ABCD-1234-EFGH-5678"

# 生成授权码
curl -X POST "https://your-api-server.com/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "30d",
    "user_email": "user@example.com"
  }'
```

## 速率限制

- 每个 IP 地址每小时最多 100 次请求
- 超过限制将返回 429 状态码
- 响应头包含 `Retry-After` 信息

## 安全注意事项

1. **HTTPS 通信**：所有 API 调用必须使用 HTTPS
2. **输入验证**：客户端应验证授权码格式
3. **错误处理**：妥善处理网络错误和 API 错误
4. **日志记录**：记录所有授权验证请求
5. **定期更新**：定期更新客户端代码以获取最新功能

## 版本历史

### v1.0.0 (2024-01-01)
- 初始版本
- 支持授权码验证和生成
- 支持多种授权类型
- 完整的错误处理

## 支持

如有问题或建议，请联系技术支持团队。
