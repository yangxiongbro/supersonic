# pip install mysql-connector-python==8.0.28
import mysql.connector
import json
import logging
import os

logger = logging.getLogger(__name__)

ss_db_info={
  "host": os.getenv("DB_HOST"),
  "port": os.getenv("DB_PORT"),
  "user": os.getenv("DB_USER"),
  "password": os.getenv("DB_PASSWORD"),
  "database": os.getenv("DB_DATABASE")
}

def connnect_mysql(ss_db_info):
  logger.info(f"连接数据库: {ss_db_info['host']}、 {ss_db_info['port']}、 {ss_db_info['user']}、 {ss_db_info['password']}、 {ss_db_info['database']}")
  return mysql.connector.connect(
    host=ss_db_info['host'],
    port=ss_db_info['port'],
    user=ss_db_info['user'],
    password=ss_db_info['password'],
    database=ss_db_info['database'],
    # charset="utf8mb4",
    auth_plugin='mysql_native_password'  # 解决认证协议问题 :ml-citation{ref="5" data="citationList"}
  )

def close_connect(conn, cursor):
  if 'cursor' in locals():
    cursor.close()
  if 'conn' in locals() and conn.is_connected():
    conn.close()
    logger.info("数据库连接已关闭")

# 执行sql
def execute_query(cursor, sql):
  logger.info(f"执行sql: {sql}")
  cursor.execute(sql)
  return cursor.fetchall()

# 执行sql
def execute_in_query(cursor, sql, inParams):
  placeholders = ', '.join(['%s'] * len(inParams))
  finalSql = sql.substitute(placeholders=placeholders)
  logger.info(f"执行sql: {finalSql}")
  cursor.execute(finalSql, tuple(inParams))
  return cursor.fetchall()

#     将一维数组切分为二维数组，每行 chunk_size 个元素
#
#     arr: 输入的一维列表或数组
#     chunk_size: 每行元素数量，默认为 100
#     返回二维列表
def split_array(arr, chunk_size=100):
  return [arr[i:i+chunk_size] for i in range(0, len(arr), chunk_size)]

# 字符串转json
def str2json(str):
  result={}
  if not str:
     return result
  try:
    result = json.loads(str)
  except Exception as e:
    logger.info(f"{str}, 字符串转json失败: {e}")
  return result