"""
软件秘钥授权系统 - 桌面PC端应用程序
使用 tkinter 和 customtkinter 创建现代化界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import sqlite3
import uuid
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import os
import sys
from pathlib import Path

# 设置 customtkinter 主题
ctk.set_appearance_mode("light")  # 可选: "light" 或 "dark"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

class LicenseManager:
    """授权码管理器"""
    
    def __init__(self, db_path: str = "licenses.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                id TEXT PRIMARY KEY,
                license_key TEXT UNIQUE NOT NULL,
                user_email TEXT,
                plan_type TEXT NOT NULL,
                start_date TEXT DEFAULT (datetime('now')),
                end_date TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON licenses(user_email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_type ON licenses(plan_type)")
        
        conn.commit()
        conn.close()
    
    def generate_license_key(self) -> str:
        """生成授权码"""
        # 生成16位随机字符串，每4位用-分隔
        chars = string.ascii_uppercase + string.digits
        key_parts = []
        for _ in range(4):
            key_parts.append(''.join(secrets.choice(chars) for _ in range(4)))
        return '-'.join(key_parts)
    
    def create_license(self, user_email: str, plan_type: str) -> Dict[str, Any]:
        """创建新授权码"""
        license_key = self.generate_license_key()
        license_id = str(uuid.uuid4())
        
        # 计算结束日期
        end_date = None
        if plan_type != "lifetime":
            days_map = {
                "trial1": 1,
                "trial3": 3,
                "30d": 30,
                "180d": 180,
                "365d": 365
            }
            days = days_map.get(plan_type, 30)
            end_date = (datetime.now() + timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO licenses (id, license_key, user_email, plan_type, end_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (license_id, license_key, user_email, plan_type, end_date, True))
        
        conn.commit()
        conn.close()
        
        return {
            "license_key": license_key,
            "user_email": user_email,
            "plan_type": plan_type,
            "end_date": end_date,
            "created_at": datetime.now().isoformat()
        }
    
    def verify_license(self, license_key: str) -> Dict[str, Any]:
        """验证授权码"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, license_key, user_email, plan_type, start_date, end_date, is_active
            FROM licenses 
            WHERE license_key = ?
        """, (license_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"status": "invalid", "message": "授权码不存在"}
        
        license_data = {
            "id": result[0],
            "license_key": result[1],
            "user_email": result[2],
            "plan_type": result[3],
            "start_date": result[4],
            "end_date": result[5],
            "is_active": bool(result[6])
        }
        
        if not license_data["is_active"]:
            return {"status": "disabled", "message": "授权码已被禁用"}
        
        if license_data["plan_type"] != "lifetime" and license_data["end_date"]:
            end_date = datetime.fromisoformat(license_data["end_date"])
            if datetime.now() > end_date:
                return {
                    "status": "expired", 
                    "message": "授权码已过期",
                    "end_date": license_data["end_date"]
                }
        
        return {
            "status": "valid",
            "message": "授权码有效",
            "plan_type": license_data["plan_type"],
            "end_date": license_data["end_date"],
            "user_email": license_data["user_email"]
        }
    
    def get_all_licenses(self) -> List[Dict[str, Any]]:
        """获取所有授权码"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT license_key, user_email, plan_type, start_date, end_date, is_active, created_at
            FROM licenses 
            ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        licenses = []
        for result in results:
            licenses.append({
                "license_key": result[0],
                "user_email": result[1],
                "plan_type": result[2],
                "start_date": result[3],
                "end_date": result[4],
                "is_active": bool(result[5]),
                "created_at": result[6]
            })
        
        return licenses
    
    def export_licenses(self, file_path: str):
        """导出授权码到文件"""
        licenses = self.get_all_licenses()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(licenses, f, ensure_ascii=False, indent=2)

class LicenseApp(ctk.CTk):
    """主应用程序类"""
    
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("软件秘钥授权系统 - 桌面版")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # 设置图标（如果有的话）
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # 初始化授权码管理器
        self.license_manager = LicenseManager()
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.refresh_license_list()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🔐 软件秘钥授权系统",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(pady=(20, 30))
        
        # 创建标签页
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 添加标签页
        self.tabview.add("生成授权码")
        self.tabview.add("验证授权码")
        self.tabview.add("管理授权码")
        self.tabview.add("系统设置")
        
        # 创建各个标签页的内容
        self.create_generate_tab()
        self.create_verify_tab()
        self.create_manage_tab()
        self.create_settings_tab()
    
    def create_generate_tab(self):
        """创建生成授权码标签页"""
        tab = self.tabview.tab("生成授权码")
        
        # 输入框架
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=20, pady=20)
        
        # 用户邮箱输入
        ctk.CTkLabel(input_frame, text="用户邮箱:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(20, 5))
        self.email_entry = ctk.CTkEntry(input_frame, placeholder_text="请输入用户邮箱", width=400, height=40)
        self.email_entry.pack(padx=20, pady=(0, 20))
        
        # 授权类型选择
        ctk.CTkLabel(input_frame, text="授权类型:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(0, 5))
        self.plan_var = tk.StringVar(value="30d")
        self.plan_menu = ctk.CTkOptionMenu(
            input_frame,
            values=["trial1", "trial3", "30d", "180d", "365d", "lifetime"],
            variable=self.plan_var,
            width=400,
            height=40
        )
        self.plan_menu.pack(padx=20, pady=(0, 20))
        
        # 生成按钮
        self.generate_btn = ctk.CTkButton(
            input_frame,
            text="🎯 生成授权码",
            command=self.generate_license,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.generate_btn.pack(pady=20)
        
        # 结果显示框架
        self.result_frame = ctk.CTkFrame(tab)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 结果标题
        self.result_title = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.result_title.pack(pady=(20, 10))
        
        # 结果内容
        self.result_text = ctk.CTkTextbox(self.result_frame, height=200)
        self.result_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_verify_tab(self):
        """创建验证授权码标签页"""
        tab = self.tabview.tab("验证授权码")
        
        # 输入框架
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=20, pady=20)
        
        # 授权码输入
        ctk.CTkLabel(input_frame, text="授权码:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(20, 5))
        self.verify_entry = ctk.CTkEntry(input_frame, placeholder_text="请输入授权码", width=400, height=40)
        self.verify_entry.pack(padx=20, pady=(0, 20))
        
        # 验证按钮
        self.verify_btn = ctk.CTkButton(
            input_frame,
            text="🔍 验证授权码",
            command=self.verify_license,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.verify_btn.pack(pady=20)
        
        # 验证结果显示
        self.verify_result_frame = ctk.CTkFrame(tab)
        self.verify_result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.verify_result_title = ctk.CTkLabel(
            self.verify_result_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.verify_result_title.pack(pady=(20, 10))
        
        self.verify_result_text = ctk.CTkTextbox(self.verify_result_frame, height=200)
        self.verify_result_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_manage_tab(self):
        """创建管理授权码标签页"""
        tab = self.tabview.tab("管理授权码")
        
        # 工具栏
        toolbar_frame = ctk.CTkFrame(tab)
        toolbar_frame.pack(fill="x", padx=20, pady=20)
        
        self.refresh_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔄 刷新",
            command=self.refresh_license_list,
            width=100
        )
        self.refresh_btn.pack(side="left", padx=10, pady=10)
        
        self.export_btn = ctk.CTkButton(
            toolbar_frame,
            text="📤 导出",
            command=self.export_licenses,
            width=100
        )
        self.export_btn.pack(side="left", padx=10, pady=10)
        
        # 授权码列表
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 创建Treeview
        columns = ("授权码", "用户邮箱", "授权类型", "状态", "有效期", "创建时间")
        self.license_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        for col in columns:
            self.license_tree.heading(col, text=col)
            self.license_tree.column(col, width=150, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.license_tree.yview)
        self.license_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.license_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_settings_tab(self):
        """创建系统设置标签页"""
        tab = self.tabview.tab("系统设置")
        
        # 设置框架
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 主题设置
        ctk.CTkLabel(settings_frame, text="界面主题:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(20, 5))
        self.theme_var = tk.StringVar(value="light")
        theme_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["light", "dark"],
            variable=self.theme_var,
            command=self.change_theme,
            width=200
        )
        theme_menu.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 数据库信息
        ctk.CTkLabel(settings_frame, text="数据库信息:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(0, 5))
        db_info = ctk.CTkLabel(settings_frame, text=f"数据库路径: {os.path.abspath(self.license_manager.db_path)}")
        db_info.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 统计信息
        ctk.CTkLabel(settings_frame, text="统计信息:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(0, 5))
        self.stats_label = ctk.CTkLabel(settings_frame, text="")
        self.stats_label.pack(anchor="w", padx=20, pady=(0, 20))
        
        # 更新统计信息
        self.update_stats()
    
    def generate_license(self):
        """生成授权码"""
        email = self.email_entry.get().strip()
        plan_type = self.plan_var.get()
        
        if not email:
            messagebox.showerror("错误", "请输入用户邮箱")
            return
        
        if not email or "@" not in email:
            messagebox.showerror("错误", "请输入有效的邮箱地址")
            return
        
        try:
            result = self.license_manager.create_license(email, plan_type)
            
            # 显示结果
            self.result_title.configure(text="✅ 授权码生成成功", text_color="green")
            
            plan_names = {
                "trial1": "1天试用",
                "trial3": "3天试用", 
                "30d": "30天授权",
                "180d": "180天授权",
                "365d": "365天授权",
                "lifetime": "永久授权"
            }
            
            result_text = f"""授权码: {result['license_key']}
用户邮箱: {result['user_email']}
授权类型: {plan_names.get(plan_type, plan_type)}
有效期至: {result['end_date'] if result['end_date'] else '永久'}
创建时间: {result['created_at']}"""
            
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", result_text)
            
            # 清空输入框
            self.email_entry.delete(0, "end")
            
            # 刷新列表
            self.refresh_license_list()
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("错误", f"生成授权码失败: {str(e)}")
    
    def verify_license(self):
        """验证授权码"""
        license_key = self.verify_entry.get().strip()
        
        if not license_key:
            messagebox.showerror("错误", "请输入授权码")
            return
        
        try:
            result = self.license_manager.verify_license(license_key)
            
            if result["status"] == "valid":
                self.verify_result_title.configure(text="✅ 授权码有效", text_color="green")
                
                plan_names = {
                    "trial1": "1天试用",
                    "trial3": "3天试用",
                    "30d": "30天授权", 
                    "180d": "180天授权",
                    "365d": "365天授权",
                    "lifetime": "永久授权"
                }
                
                result_text = f"""状态: 有效
授权类型: {plan_names.get(result['plan_type'], result['plan_type'])}
有效期至: {result['end_date'] if result['end_date'] else '永久'}
用户邮箱: {result['user_email'] or '未绑定'}"""
                
            elif result["status"] == "expired":
                self.verify_result_title.configure(text="⏰ 授权码已过期", text_color="orange")
                result_text = f"""状态: 已过期
过期时间: {result['end_date']}"""
                
            elif result["status"] == "disabled":
                self.verify_result_title.configure(text="❌ 授权码已禁用", text_color="red")
                result_text = f"""状态: 已禁用
原因: {result['message']}"""
                
            else:
                self.verify_result_title.configure(text="❌ 授权码无效", text_color="red")
                result_text = f"""状态: 无效
原因: {result['message']}"""
            
            self.verify_result_text.delete("1.0", "end")
            self.verify_result_text.insert("1.0", result_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"验证授权码失败: {str(e)}")
    
    def refresh_license_list(self):
        """刷新授权码列表"""
        try:
            # 清空现有数据
            for item in self.license_tree.get_children():
                self.license_tree.delete(item)
            
            # 获取所有授权码
            licenses = self.license_manager.get_all_licenses()
            
            plan_names = {
                "trial1": "1天试用",
                "trial3": "3天试用",
                "30d": "30天授权",
                "180d": "180天授权", 
                "365d": "365天授权",
                "lifetime": "永久授权"
            }
            
            for license_data in licenses:
                # 格式化日期
                end_date = license_data['end_date'] if license_data['end_date'] else '永久'
                created_at = license_data['created_at'][:19] if license_data['created_at'] else ''
                
                # 状态
                status = "有效" if license_data['is_active'] else "禁用"
                if license_data['is_active'] and license_data['end_date']:
                    end_dt = datetime.fromisoformat(license_data['end_date'])
                    if datetime.now() > end_dt:
                        status = "过期"
                
                self.license_tree.insert("", "end", values=(
                    license_data['license_key'],
                    license_data['user_email'] or '',
                    plan_names.get(license_data['plan_type'], license_data['plan_type']),
                    status,
                    end_date,
                    created_at
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新列表失败: {str(e)}")
    
    def export_licenses(self):
        """导出授权码"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="导出授权码"
            )
            
            if file_path:
                self.license_manager.export_licenses(file_path)
                messagebox.showinfo("成功", f"授权码已导出到: {file_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def change_theme(self, theme):
        """切换主题"""
        ctk.set_appearance_mode(theme)
    
    def update_stats(self):
        """更新统计信息"""
        try:
            licenses = self.license_manager.get_all_licenses()
            total = len(licenses)
            active = sum(1 for l in licenses if l['is_active'])
            expired = sum(1 for l in licenses if l['is_active'] and l['end_date'] and datetime.fromisoformat(l['end_date']) < datetime.now())
            
            stats_text = f"""总授权码数: {total}
有效授权码: {active}
过期授权码: {expired}"""
            
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            self.stats_label.configure(text=f"统计信息获取失败: {str(e)}")

def main():
    """主函数"""
    app = LicenseApp()
    app.mainloop()

if __name__ == "__main__":
    main()

