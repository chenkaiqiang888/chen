/*
C#客户端示例 - 软件授权验证
*/
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace LicenseClient
{
    public class LicenseVerificationResult
    {
        public string Status { get; set; }
        public string PlanType { get; set; }
        public DateTime? EndDate { get; set; }
        public string UserEmail { get; set; }
        public string Message { get; set; }
    }

    public class LicenseClient
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiBaseUrl;

        public LicenseClient(string apiBaseUrl)
        {
            _apiBaseUrl = apiBaseUrl.TrimEnd('/');
            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "LicenseClient/1.0");
        }

        public async Task<LicenseVerificationResult> VerifyLicenseAsync(string licenseKey)
        {
            try
            {
                string url = $"{_apiBaseUrl}/verify/{licenseKey}";
                HttpResponseMessage response = await _httpClient.GetAsync(url);
                
                if (response.IsSuccessStatusCode)
                {
                    string jsonContent = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<LicenseVerificationResult>(jsonContent);
                }
                else
                {
                    return new LicenseVerificationResult
                    {
                        Status = "error",
                        Message = $"API请求失败: {response.StatusCode}"
                    };
                }
            }
            catch (Exception ex)
            {
                return new LicenseVerificationResult
                {
                    Status = "error",
                    Message = $"验证失败: {ex.Message}"
                };
            }
        }

        public async Task<bool> CheckLicenseStatusAsync(string licenseKey)
        {
            var result = await VerifyLicenseAsync(licenseKey);
            return result.Status == "valid";
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            // 配置API服务器地址
            string apiBaseUrl = "https://your-api-server.com"; // 替换为实际的API地址
            
            // 创建客户端
            var client = new LicenseClient(apiBaseUrl);
            
            Console.WriteLine("=== 软件授权验证系统 ===");
            Console.WriteLine("请输入您的授权码:");
            
            // 获取用户输入的授权码
            string licenseKey = Console.ReadLine()?.Trim();
            
            if (string.IsNullOrEmpty(licenseKey))
            {
                Console.WriteLine("错误: 授权码不能为空");
                Environment.Exit(1);
            }
            
            Console.WriteLine($"\n正在验证授权码: {licenseKey}");
            Console.WriteLine("请稍候...");
            
            // 验证授权码
            var result = await client.VerifyLicenseAsync(licenseKey);
            
            // 显示结果
            Console.WriteLine("\n=== 验证结果 ===");
            
            switch (result.Status)
            {
                case "valid":
                    Console.WriteLine("✅ 授权码验证成功!");
                    Console.WriteLine($"授权类型: {result.PlanType ?? "未知"}");
                    
                    if (result.EndDate.HasValue)
                    {
                        Console.WriteLine($"到期时间: {result.EndDate.Value:yyyy-MM-dd HH:mm:ss}");
                    }
                    else
                    {
                        Console.WriteLine("授权类型: 永久使用权");
                    }
                    
                    if (!string.IsNullOrEmpty(result.UserEmail))
                    {
                        Console.WriteLine($"绑定邮箱: {result.UserEmail}");
                    }
                    
                    Console.WriteLine("\n软件启动成功! 欢迎使用!");
                    break;
                    
                case "expired":
                    Console.WriteLine("❌ 授权码已过期");
                    Console.WriteLine("请联系管理员续费或购买新的授权码");
                    break;
                    
                case "disabled":
                    Console.WriteLine("❌ 授权码已被禁用");
                    Console.WriteLine("请联系管理员了解详情");
                    break;
                    
                case "not_found":
                    Console.WriteLine("❌ 授权码不存在");
                    Console.WriteLine("请检查授权码是否正确");
                    break;
                    
                default:
                    Console.WriteLine("❌ 验证失败");
                    Console.WriteLine($"错误信息: {result.Message ?? "未知错误"}");
                    break;
            }
            
            // 根据验证结果决定是否退出
            if (result.Status != "valid")
            {
                Console.WriteLine("\n软件无法启动，请解决授权问题后重试。");
                Environment.Exit(1);
            }
            
            Console.WriteLine("\n按任意键退出...");
            Console.ReadKey();
        }
    }
}
