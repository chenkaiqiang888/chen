"""
数据库连接管理
支持SQLite（本地开发）和PostgreSQL（生产环境）
"""
import os
import sqlite3
import psycopg2
from contextlib import contextmanager
from typing import Generator, Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///license_system.db")
        self.is_postgresql = self.database_url.startswith("postgresql://")
        
        if self.is_postgresql:
            logger.info("Using PostgreSQL database")
        else:
            # SQLite配置
            if self.database_url.startswith("sqlite:///"):
                self.db_path = self.database_url.replace("sqlite:///", "")
            else:
                self.db_path = "license_system.db"
            logger.info("Using SQLite database")
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            if self.is_postgresql:
                # PostgreSQL初始化
                with psycopg2.connect(self.database_url) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS licenses (
                                id VARCHAR(255) PRIMARY KEY,
                                license_key VARCHAR(255) UNIQUE NOT NULL,
                                user_email VARCHAR(255),
                                plan_type VARCHAR(50) NOT NULL CHECK (plan_type IN ('trial1', 'trial3', '30d', '180d', '365d', 'lifetime')),
                                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                end_date TIMESTAMP,
                                is_active BOOLEAN DEFAULT TRUE,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        
                        # 创建索引
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key)")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON licenses(user_email)")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_type ON licenses(plan_type)")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_active ON licenses(is_active)")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_end_date ON licenses(end_date)")
                        
                        conn.commit()
            else:
                # SQLite初始化
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS licenses (
                            id TEXT PRIMARY KEY,
                            license_key TEXT UNIQUE NOT NULL,
                            user_email TEXT,
                            plan_type TEXT NOT NULL CHECK (plan_type IN ('trial1', 'trial3', '30d', '180d', '365d', 'lifetime')),
                            start_date TEXT DEFAULT (datetime('now')),
                            end_date TEXT,
                            is_active BOOLEAN DEFAULT 1,
                            created_at TEXT DEFAULT (datetime('now')),
                            updated_at TEXT DEFAULT (datetime('now'))
                        )
                    """)
                    
                    # 创建索引
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_license_key ON licenses(license_key)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON licenses(user_email)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_plan_type ON licenses(plan_type)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_is_active ON licenses(is_active)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_end_date ON licenses(end_date)")
                    
                    conn.commit()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = None
        try:
            if self.is_postgresql:
                conn = psycopg2.connect(self.database_url)
                yield conn
            else:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row  # 使结果可以像字典一样访问
                yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if cursor.description:
                if self.is_postgresql:
                    # PostgreSQL返回字典格式
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                else:
                    # SQLite返回字典格式
                    return [dict(row) for row in cursor.fetchall()]
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作并返回影响的行数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = None) -> str:
        """执行插入操作并返回插入的ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return str(cursor.lastrowid) if cursor.lastrowid else None


# 全局数据库管理器实例
db_manager = DatabaseManager()
