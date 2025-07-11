import os
from sync_data.sync_data_common import logger, connnect_mysql, close_connect, execute_query, execute_in_query, split_array, str2json
import pandasai as pai
import re
from pandasai.helpers.path import get_validated_dataset_path
from pandasai.config import ConfigManager
import shutil
from string import Template

config = ConfigManager()

# 获取schema path
def get_path(database_id, table_name, domain_id):
  return f"db-{database_id}/{domain_id}-{re.sub(r'[^a-zA-Z0-9]+', '-', table_name)}".lower()

# 创建 schema
def create_schema(schema_infos):
  logger.info(f"create_schema")
  paths = []
  for schema_info in schema_infos:
    try:
      path=get_path(schema_info["database_id"], schema_info["table_name"], schema_info["domain_id"])
      logger.info(f"create_schema path: {path}")
      logger.info(f"create_schema schema_info: {schema_info}")

      delete_schema_by_path(path)
      sql_table = pai.create(
          # Format: "organization/dataset"
          path=path,

          # Optional description
          description=schema_info["description"],

          # Define the source of the data, including connection details and
          # table name
          source=schema_info["source"],
          columns=schema_info["columns"],
          relations=schema_info["relations"]
      )
      logger.info(f"pai.create result: {sql_table}")
      paths.append(path)
    except Exception as e:
      logger.exception(f"创建schema失败: {e}")
  return paths

# 根据模型id删除schema
def delete_schema(ss_db_info, model_ids):
  result = []
  paths = get_paths(ss_db_info, model_ids)
  for path in paths:
    if delete_schema_by_path(path):
      result.append(path)
  return result

# 根据path删除schema
def delete_schema_by_path(path):
  result = False
  try:
    org_name, dataset_name = get_validated_dataset_path(path)
    dataset_directory = str(os.path.join(org_name, dataset_name))

    file_manager = config.get().file_manager
    if file_manager.exists(dataset_directory):
      shutil.rmtree(file_manager.abs_path(dataset_directory))
    result = True
  except Exception as e:
    logger.exception(f"删除schema失败,path={path}: {e}")
  return result

# 更新 schema
def update_schema(schema_infos):
  return create_schema(schema_infos)

def get_paths(ss_db_info, model_ids):
  conn = connnect_mysql(ss_db_info)
  cursor = conn.cursor(dictionary=True)
  
  paths = []
  for part_model_ids in split_array(sorted(model_ids)):
    try:
      # 查询模型表
      model_rows = execute_in_query(cursor, Template("""
                                    select 
                                      model.biz_name as biz_name, 
                                      model.domain_id as domain_id,
                                      model.model_detail as model_detail, 
                                      model.database_id as database_id
                                    from s2_model model
                                    where model.id in ($placeholders)
                                    """), part_model_ids)
      for model_row in model_rows:
        # 封装模型信息
        model_details = str2json(model_row.get("model_detail", "\{\}"))
        table_name = model_details.get("tableQuery", "").lower() if "table_query" == model_details.get("queryType", "").lower() else model_row.get("biz_name", "")
        paths.append(get_path(model_row["database_id"], table_name, model_row["domain_id"]))
    except Exception as e:
      logger.exception(f"查询模型信息失败,part_model_ids={part_model_ids}， Exception={e}")
    finally:
      close_connect(conn, cursor)
  return paths
   

def get_terms(ss_db_info, model_ids):
  conn = connnect_mysql(ss_db_info)
  cursor = conn.cursor(dictionary=True)
  
  terms = []
  for part_model_ids in split_array(sorted(model_ids)):
    try:
      # 查询模型表
      term_rows = execute_in_query(cursor, Template("""
                                    select 
                                      term.name as name, 
                                      term.description as description, 
                                      term.alias as alias_json_str
                                    from s2_term term
                                    where exists (
                                      select 1 from s2_model model where model.id in ($placeholders) and term.domain_id = model.domain_id
                                    )
                                    """), part_model_ids)
      for term_row in term_rows:
        term_row["alias"] = "或".join(str2json(term_row["alias_json_str"])) 
      terms.extend(term_rows)
    except Exception as e:
      logger.exception(f"查询术语信息失败,part_model_ids={part_model_ids}, Exception={e}")
    finally:
      close_connect(conn, cursor)

  return terms
