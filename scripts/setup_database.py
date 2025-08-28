#!/usr/bin/env python3
"""
数据库设置脚本
用于初始化数据库表结构和示例数据
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_database_connection():
    """获取数据库连接"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("错误: 未设置 DATABASE_URL 环境变量")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)


def execute_sql_file(conn, file_path):
    """执行SQL文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        
        print(f"✅ 成功执行: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 执行失败 {file_path}: {e}")
        conn.rollback()
        return False


def create_sample_data(conn):
    """创建示例数据"""
    sample_data = [
        {
            'license_key': 'DEMO-TRIAL1-ABCD1234',
            'user_email': 'demo@example.com',
            'plan_type': 'trial1',
            'end_date': "NOW() + INTERVAL '1 day'"
        },
        {
            'license_key': 'DEMO-TRIAL3-EFGH5678',
            'user_email': 'demo@example.com',
            'plan_type': 'trial3',
            'end_date': "NOW() + INTERVAL '3 days'"
        },
        {
            'license_key': 'DEMO-30D-IJKL9012',
            'user_email': 'demo@example.com',
            'plan_type': '30d',
            'end_date': "NOW() + INTERVAL '30 days'"
        },
        {
            'license_key': 'DEMO-180D-MNOP3456',
            'user_email': 'demo@example.com',
            'plan_type': '180d',
            'end_date': "NOW() + INTERVAL '180 days'"
        },
        {
            'license_key': 'DEMO-365D-QRST7890',
            'user_email': 'demo@example.com',
            'plan_type': '365d',
            'end_date': "NOW() + INTERVAL '365 days'"
        },
        {
            'license_key': 'DEMO-LIFETIME-UVWX1234',
            'user_email': 'demo@example.com',
            'plan_type': 'lifetime',
            'end_date': 'NULL'
        }
    ]
    
    try:
        cursor = conn.cursor()
        
        for data in sample_data:
            query = """
            INSERT INTO licenses (license_key, user_email, plan_type, end_date)
            VALUES (%(license_key)s, %(user_email)s, %(plan_type)s, %(end_date)s)
            ON CONFLICT (license_key) DO NOTHING
            """
            
            # 处理end_date
            if data['end_date'] == 'NULL':
                query = """
                INSERT INTO licenses (license_key, user_email, plan_type, end_date)
                VALUES (%(license_key)s, %(user_email)s, %(plan_type)s, NULL)
                ON CONFLICT (license_key) DO NOTHING
                """
                cursor.execute(query, {
                    'license_key': data['license_key'],
                    'user_email': data['user_email'],
                    'plan_type': data['plan_type']
                })
            else:
                cursor.execute(query, data)
        
        conn.commit()
        cursor.close()
        
        print("✅ 成功创建示例数据")
        return True
        
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        conn.rollback()
        return False


def verify_setup(conn):
    """验证设置"""
    try:
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'licenses'
        """)
        
        if not cursor.fetchone():
            print("❌ licenses表不存在")
            return False
        
        # 检查记录数量
        cursor.execute("SELECT COUNT(*) FROM licenses")
        count = cursor.fetchone()[0]
        
        print(f"✅ 数据库设置完成，共有 {count} 条授权码记录")
        
        # 显示示例授权码
        cursor.execute("""
            SELECT license_key, plan_type, end_date 
            FROM licenses 
            ORDER BY created_at 
            LIMIT 5
        """)
        
        print("\n示例授权码:")
        for row in cursor.fetchall():
            license_key, plan_type, end_date = row
            print(f"  {license_key} - {plan_type} - {end_date or '永久'}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def main():
    """主函数"""
    print("=== 数据库设置脚本 ===")
    
    # 获取数据库连接
    conn = get_database_connection()
    
    try:
        # 执行SQL文件
        schema_file = "database/schema.sql"
        if os.path.exists(schema_file):
            if execute_sql_file(conn, schema_file):
                print("✅ 数据库表结构创建成功")
            else:
                print("❌ 数据库表结构创建失败")
                return
        else:
            print(f"❌ 找不到文件: {schema_file}")
            return
        
        # 创建示例数据
        if create_sample_data(conn):
            print("✅ 示例数据创建成功")
        else:
            print("❌ 示例数据创建失败")
            return
        
        # 验证设置
        if verify_setup(conn):
            print("\n🎉 数据库设置完成!")
        else:
            print("\n❌ 数据库设置验证失败")
            
    finally:
        conn.close()


if __name__ == "__main__":
    main()
