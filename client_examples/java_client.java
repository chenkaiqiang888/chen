/*
Java客户端示例 - 软件授权验证
*/
import java.io.*;
import java.net.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;

public class LicenseClient {
    
    private final String apiBaseUrl;
    private final ObjectMapper objectMapper;
    
    public LicenseClient(String apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl.replaceAll("/$", "");
        this.objectMapper = new ObjectMapper();
    }
    
    public static class LicenseVerificationResult {
        @JsonProperty("status")
        private String status;
        
        @JsonProperty("plan_type")
        private String planType;
        
        @JsonProperty("end_date")
        private String endDate;
        
        @JsonProperty("user_email")
        private String userEmail;
        
        @JsonProperty("message")
        private String message;
        
        // Getters and Setters
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        
        public String getPlanType() { return planType; }
        public void setPlanType(String planType) { this.planType = planType; }
        
        public String getEndDate() { return endDate; }
        public void setEndDate(String endDate) { this.endDate = endDate; }
        
        public String getUserEmail() { return userEmail; }
        public void setUserEmail(String userEmail) { this.userEmail = userEmail; }
        
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
    }
    
    public LicenseVerificationResult verifyLicense(String licenseKey) {
        try {
            String url = apiBaseUrl + "/verify/" + URLEncoder.encode(licenseKey, "UTF-8");
            URL apiUrl = new URL(url);
            HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
            
            // 设置请求属性
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("User-Agent", "LicenseClient/1.0");
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            
            int responseCode = connection.getResponseCode();
            
            if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(connection.getInputStream())
                );
                StringBuilder response = new StringBuilder();
                String line;
                
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                
                return objectMapper.readValue(response.toString(), LicenseVerificationResult.class);
            } else {
                LicenseVerificationResult errorResult = new LicenseVerificationResult();
                errorResult.setStatus("error");
                errorResult.setMessage("API请求失败: " + responseCode);
                return errorResult;
            }
            
        } catch (Exception e) {
            LicenseVerificationResult errorResult = new LicenseVerificationResult();
            errorResult.setStatus("error");
            errorResult.setMessage("验证失败: " + e.getMessage());
            return errorResult;
        }
    }
    
    public boolean checkLicenseStatus(String licenseKey) {
        LicenseVerificationResult result = verifyLicense(licenseKey);
        return "valid".equals(result.getStatus());
    }
    
    public static void main(String[] args) {
        // 配置API服务器地址
        String apiBaseUrl = "https://your-api-server.com"; // 替换为实际的API地址
        
        // 创建客户端
        LicenseClient client = new LicenseClient(apiBaseUrl);
        
        System.out.println("=== 软件授权验证系统 ===");
        System.out.println("请输入您的授权码:");
        
        // 获取用户输入的授权码
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        String licenseKey;
        
        try {
            licenseKey = reader.readLine().trim();
            
            if (licenseKey.isEmpty()) {
                System.out.println("错误: 授权码不能为空");
                System.exit(1);
            }
            
            System.out.println("\n正在验证授权码: " + licenseKey);
            System.out.println("请稍候...");
            
            // 验证授权码
            LicenseVerificationResult result = client.verifyLicense(licenseKey);
            
            // 显示结果
            System.out.println("\n=== 验证结果 ===");
            
            switch (result.getStatus()) {
                case "valid":
                    System.out.println("✅ 授权码验证成功!");
                    System.out.println("授权类型: " + (result.getPlanType() != null ? result.getPlanType() : "未知"));
                    
                    if (result.getEndDate() != null && !result.getEndDate().isEmpty()) {
                        System.out.println("到期时间: " + result.getEndDate());
                    } else {
                        System.out.println("授权类型: 永久使用权");
                    }
                    
                    if (result.getUserEmail() != null && !result.getUserEmail().isEmpty()) {
                        System.out.println("绑定邮箱: " + result.getUserEmail());
                    }
                    
                    System.out.println("\n软件启动成功! 欢迎使用!");
                    break;
                    
                case "expired":
                    System.out.println("❌ 授权码已过期");
                    System.out.println("请联系管理员续费或购买新的授权码");
                    break;
                    
                case "disabled":
                    System.out.println("❌ 授权码已被禁用");
                    System.out.println("请联系管理员了解详情");
                    break;
                    
                case "not_found":
                    System.out.println("❌ 授权码不存在");
                    System.out.println("请检查授权码是否正确");
                    break;
                    
                default:
                    System.out.println("❌ 验证失败");
                    System.out.println("错误信息: " + (result.getMessage() != null ? result.getMessage() : "未知错误"));
                    break;
            }
            
            // 根据验证结果决定是否退出
            if (!"valid".equals(result.getStatus())) {
                System.out.println("\n软件无法启动，请解决授权问题后重试。");
                System.exit(1);
            }
            
        } catch (IOException e) {
            System.out.println("输入错误: " + e.getMessage());
            System.exit(1);
        }
        
        System.out.println("\n按回车键退出...");
        try {
            reader.readLine();
        } catch (IOException e) {
            // 忽略
        }
    }
}
