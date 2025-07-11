import os
import time
import json
from .dbmanager import DatabaseManager
from pandasai.dataframe import DataFrame
from datetime import datetime
import yaml
import shutil
import pandas as pd
import pandasai as pai
from typing import List, Union, Optional, Dict, Any
from pandasai.helpers.path import (
    find_dataset_base_path
)
import logging
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class DatasetManager:
    """数据集管理器"""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.datasets = {}
        self.datasets_dir = find_dataset_base_path()
        self.dataset_schema_file_name="schema.yaml"
        self.load_datasets()
    
    def load_datasets(self):
        self.datasets.clear()
        """加载所有数据集信息"""
        os.makedirs(self.datasets_dir, exist_ok=True)
        
        for org in os.listdir(self.datasets_dir):
            for dsname in os.listdir(os.path.join(self.datasets_dir,org)):
                schema_file_path=os.path.join(self.datasets_dir,org,dsname,self.dataset_schema_file_name)
                parquet_file_path=os.path.join(self.datasets_dir,org,dsname,"data.parquet")
                if os.path.isdir(os.path.join(self.datasets_dir,org,dsname)) and os.path.exists(schema_file_path) and  os.path.exists(parquet_file_path):
                    # 读取schema.yaml
                    schema=yaml.safe_load(schema_file_path)
                    dataset_name=org+"/"+dsname
                    self.datasets[dataset_name] = {
                        'path': os.path.join(self.datasets_dir, org),
                        'created_at': datetime.fromtimestamp(os.path.getmtime(schema_file_path)),
                        'size': os.path.getsize(parquet_file_path)
                    }                
        logger.info(f"已加载 {len(self.datasets)} 个数据集")       
    
    def create_dataset(self, file_path: str, dataset_name: str = None) -> str:
        name=os.path.basename(file_path).split('.')[0]
        name=name.split("_")[1]
        """创建新数据集"""
        if not dataset_name:
            dataset_name = os.path.join("myorg",name)
      
        try:
            # 读取并重新保存文件，确保格式正确
            df = pd.read_csv(file_path)
            # df.to_csv(save_csv_path, index=False)           
            pdf=DataFrame(df)
            pai.create(path=dataset_name,
                description=name,
                df = pdf
            )
            
            # 创建数据库表
            # conn = self.db_manager.connect(dataset_name)
            # conn.execute(f"CREATE TABLE IF NOT EXISTS {dataset_name} AS SELECT * FROM df")
            
            # 记录数据集信息
            self.datasets[dataset_name] = {
                'path': dataset_name+"/data.parquet",
                'created_at': datetime.now(),
                'size': os.path.getsize(os.path.join(self.datasets_dir, dataset_name, "data.parquet"))
            }
            
            logger.info(f"已创建数据集: {dataset_name}")
            return dataset_name
        except Exception as e:
            logger.error(f"创建数据集失败: {e}")
            raise

    def create_db_dataset_schema(self, org: str, dataset_name: str,schema_json:str):
        # 验证数据是否合规
        if org is None or org=='':
            raise("org不能为空")
        if dataset_name is None or dataset_name=='':
            raise("dataset_name不能为空") 
        if schema_json is None or schema_json=='':
            raise("schema_json不能为空")       
         
        

        schema_dir_path=os.path.join(self.datasets_dir,org,dataset_name)
        schema_file_path=os.path.join(schema_dir_path,self.dataset_schema_file_name)
        # 查看目录是否已经存在
        if os.path.isdir(schema_dir_path):
            # 如果schema.yaml存在则先备份
            if os.path.exists(schema_file_path):
                milliseconds_since_epoch = int(time.time() * 1000)
                os.rename(schema_file_path,schema_file_path+f".{milliseconds_since_epoch}")
        else:
            os.makedirs(schema_dir_path)
        # 创建新的schema.yaml     
        try:
            pai.create(path=schema_dir_path,source=json.loads(schema_json)) 
            return dataset_name
        except Exception as e:
            logger.error(f"创建数据集失败: {e}")
            raise

    
    
    
    def delete_dataset(self, dataset_name: str):
        """删除数据集"""
        if dataset_name in self.datasets:
            dataset_path = os.path.join(self.datasets_dir,dataset_name)
            if os.path.exists(dataset_path):
                shutil.rmtree(dataset_path)
                logger.info(f"已删除目录: {dataset_path}")
            else:
                logger.warning(f"目录不存在: {dataset_path}")
            self.datasets.pop(dataset_name)
            self.db_manager.close(dataset_name)
            
            logger.info(f"已删除数据集: {dataset_name}")
        else:
            logger.warning(f"尝试删除不存在的数据集: {dataset_name}")
    
    def get_dataset_list(self) -> List[Dict]:
        """获取数据集列表"""

        return [{'name': name, **info} for name, info in self.datasets.items()]
    
    def get_dataset_preview(self, dataset_name: str, limit: int = 10) -> pd.DataFrame:
        """获取数据集预览"""
        if dataset_name not in self.datasets:
            raise ValueError(f"数据集 {dataset_name} 不存在")          
        try:
            dataset_parts = dataset_name.split("/")
            # 处理分割后的数组
            if len(dataset_parts) > 1:
                table_name = dataset_parts[1]
            else:
                logger.warning(f"dataset_name 没有包含 '/': {table_name}")
                table_name = dataset_parts[0]
            df=pai.load(dataset_name)
            return df
            # sql = f"SELECT * FROM {table_name} LIMIT {limit}"
            # return self.db_manager.query(dataset_name, sql)
       
        except Exception as e:
            logger.error(f"获取数据集预览失败: {e}")
            raise