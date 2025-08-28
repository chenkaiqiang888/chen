# 客户端示例

本目录包含多种编程语言的客户端示例，展示如何集成软件授权验证功能。

## 支持的语言

- **Python** (`python_client.py`) - 简单易用，适合快速集成
- **C#** (`csharp_client.cs`) - 适用于.NET应用程序
- **Java** (`java_client.java`) - 适用于Java应用程序

## 使用方法

### 1. Python客户端

```bash
# 安装依赖
pip install requests

# 运行示例
python python_client.py
```

### 2. C#客户端

```bash
# 安装依赖包
dotnet add package Newtonsoft.Json
dotnet add package System.Net.Http

# 编译运行
dotnet run
```

### 3. Java客户端

```bash
# 安装依赖
# 需要添加 Jackson 库到 classpath

# 编译运行
javac -cp ".:jackson-core.jar:jackson-databind.jar:jackson-annotations.jar" java_client.java
java -cp ".:jackson-core.jar:jackson-databind.jar:jackson-annotations.jar" LicenseClient
```

## 集成到您的软件

### 基本集成步骤

1. **复制客户端代码**到您的项目中
2. **修改API地址**为您的实际服务器地址
3. **在软件启动时调用验证函数**
4. **根据验证结果决定软件行为**

### 示例集成代码

```python
# Python示例
from client_examples.python_client import LicenseClient

def main():
    client = LicenseClient("https://your-api-server.com")
    
    # 获取用户输入的授权码
    license_key = input("请输入授权码: ")
    
    # 验证授权码
    result = client.verify_license(license_key)
    
    if result["status"] == "valid":
        print("授权验证成功，启动软件...")
        # 启动您的软件主功能
        start_software()
    else:
        print("授权验证失败，软件无法启动")
        exit(1)
```

## 安全建议

1. **使用HTTPS**：确保与API服务器的通信使用HTTPS
2. **输入验证**：验证用户输入的授权码格式
3. **错误处理**：妥善处理网络错误和API错误
4. **缓存机制**：可以考虑缓存验证结果，避免频繁请求
5. **离线模式**：考虑实现离线验证机制（可选）

## 自定义配置

### 超时设置
```python
# Python示例
client.session.timeout = 10  # 10秒超时
```

### 重试机制
```python
import time

def verify_with_retry(client, license_key, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = client.verify_license(license_key)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # 指数退避
```

## 常见问题

### Q: 如何处理网络连接失败？
A: 实现重试机制和离线模式，或者提示用户检查网络连接。

### Q: 授权码验证失败怎么办？
A: 显示具体的错误信息，引导用户联系管理员或重新输入授权码。

### Q: 如何实现自动续费提醒？
A: 检查授权码的到期时间，在到期前提醒用户续费。

## 技术支持

如果您在集成过程中遇到问题，请：

1. 检查API服务器地址是否正确
2. 确认网络连接正常
3. 查看错误日志获取详细信息
4. 联系技术支持团队
