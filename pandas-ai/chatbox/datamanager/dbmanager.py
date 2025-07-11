import os
import pandas as pd
from pandasai.helpers.path import (
    find_dataset_base_path
)
import duckdb
import logging
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class DatabaseManager:
    """数据库管理器"""
    def __init__(self):
        self.connections = {}
        self.base_dir = find_dataset_base_path()
        os.makedirs(self.base_dir, exist_ok=True)
    
    def connect(self, db_name: str) -> duckdb.DuckDBPyConnection:
        """连接到数据库"""
        if db_name not in self.connections:
            db_path = os.path.join(self.base_dir,db_name, "data.parquet")
            self.connections[db_name] = duckdb.connect(db_path)
            logger.info(f"已连接到数据库: {db_name}")
        return self.connections[db_name]
    
    def query(self, db_name: str, sql: str) -> pd.DataFrame:
        """执行查询"""
        conn = self.connect(db_name)
        try:
            result = conn.execute(sql).fetchdf()
            logger.info(f"执行查询成功: {sql}")
            return result
        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise
    
    def close(self, db_name: str):
        """关闭数据库连接"""
        if db_name in self.connections:
            self.connections[db_name].close()
            del self.connections[db_name]
            logger.info(f"已关闭数据库连接: {db_name}")
    
    def close_all(self):
        """关闭所有数据库连接"""
        for db_name in list(self.connections.keys()):
            self.close(db_name)