from sync_data.sync_data_common import logger, ss_db_info, connnect_mysql, close_connect, execute_query, execute_in_query, str2json
from sync_data.sync_schema import get_paths, get_terms
from string import Template
from extensions.llms.openai.pandasai_openai import OpenAI
from chatbox.agents.agents import *
import random

# 获取助手信息
def get_agent_info(agent_id):
  agent_infos = get_agent_infos(agent_ids=[agent_id])
  if len(agent_infos) > 0:
    return agent_infos[0]
  raise Exception(f"没有找到id={agent_id}的助手信息")

# 获取助手信息
def get_agent_infos(agent_ids):
  agent_infos = []
  conn = connnect_mysql(ss_db_info)
  cursor = conn.cursor(dictionary=True)
  try:
    agent_rows = execute_in_query(cursor, Template(f"select id, name, description, tool_config, chat_model_config from s2_agent where id in($placeholders)"), agent_ids)
    for agent_row in agent_rows:
      logger.info(f"解析助手信息id={agent_row['id']}")
      data_set_ids = set()
      tool_config = str2json(agent_row["tool_config"])
      # 获取某个助手的数据集ID
      for tool in tool_config.get("tools", []):
        if "DATASET" == tool["type"]:
          data_set_ids.update(tool.get("dataSetIds",[]))
      logger.info(f"data_set_ids:{data_set_ids}")

      if not data_set_ids:
        raise Exception(f"该助手没有配置数据集")

      # 根据数据集ID获取模型ID
      data_set_rows = execute_in_query(cursor, Template("select data_set_detail from s2_data_set where id in($placeholders)"), data_set_ids)
      model_ids = set()
      for data_set_row in data_set_rows:
        data_set_detail = str2json(data_set_row["data_set_detail"])
        model_ids.update([item["id"] for item in data_set_detail.get("dataSetModelConfigs", [])])
      logger.info(f"model_ids:{model_ids}")

      # 模型schema路径
      datasets = get_paths(ss_db_info, model_ids)
      # 术语
      terms = get_terms(ss_db_info, model_ids)

      chat_model_config = str2json(agent_row["chat_model_config"])
      llm_dict, instruction_dict = parse_model_config(cursor, chat_model_config)
      agent_infos.append({
        "name": agent_row["name"], 
        "role": agent_row["description"], 
        "datasets": datasets, 
        "terms": terms,
        "llm": llm_dict.get("llm", None), 
        "correct_llm": llm_dict.get("correct_llm", None), 
        "instructions": instruction_dict
      })
  finally:
    close_connect(conn, cursor)
  return agent_infos

# 解析大模型配置和指令配置
def parse_model_config(cursor, chat_model_config):
  llm_dict = {}
  instruction_dict={}
  sql_parse = chat_model_config["S2SQL_PARSER"]
  if sql_parse["enable"]:
    llm_dict["llm"] = get_llm(cursor, sql_parse.get("chatModelId", None))
    instruction_dict["S2SQL_PARSER"] = sql_parse.get("prompt", "")
  sql_corrector = chat_model_config["S2SQL_CORRECTOR"]
  if sql_corrector["enable"]:
    llm_dict["correct_llm"] = get_llm(cursor, sql_corrector.get("chatModelId", None))
    instruction_dict["S2SQL_CORRECTOR"] = sql_corrector.get("prompt", "")
  return llm_dict, instruction_dict
  
def get_llm(cursor, chat_model_id):
  if not chat_model_id:
    raise Exception(f"该助手没有配置大模型")
  rows = execute_query(cursor, f"select name, config from s2_chat_model where id={chat_model_id}")
  if len(rows) <= 0:
    raise Exception(f"该助手没有配置大模型")
  row = rows[0]
  config = str2json(row["config"])
  if config["provider"] != "OPEN_AI":
    raise Exception(f"不支持的大模型类型：{config['provider']}")
  
  logger.info(f"llm config:{row}")
  OpenAI._supported_chat_models.append(config["modelName"])
  return OpenAI(
    max_tokens=config.get("maxTokens", 8192),
    temperature=config.get("temperature", 0),
    model=config["modelName"],
    api_token=config["apiKey"],
    api_base=config["baseUrl"])

# agent缓存
agent_map={}

# 根据助手id获取一个助手
def get_agent(agent_id, chat_id):
  agent = None
  chat_id = chat_id if chat_id else random.randint(1, 1000000)
  # 根据agent_id获取助手字典
  chat_agent_map = agent_map.get(agent_id)
  if chat_agent_map is None:
    chat_agent_map = {}
    agent_map[agent_id] = chat_agent_map
  
  # 根据chat_id获取助手
  agent = chat_agent_map.get(chat_id)
  if agent is None:
    logger.info(f"缓存中没有找到助手：agent_id：{agent_id}，chat_id：{chat_id}")
    agent_info = get_agent_info(agent_id)
    logger.info(f"agent_info: {agent_info}")
    agent = DataAnalysisAgentMarkdown(
      name=agent_info["name"],
      role=agent_info["role"],
      llm=agent_info["llm"],
      correct_llm=agent_info["correct_llm"],
      datasets=agent_info["datasets"],
      terms=agent_info["terms"],
      instructions=agent_info["instructions"],
      avatar="https://cdn.quasar.dev/img/avatar4.jpg")
    chat_agent_map[chat_id] = agent
  else:
    logger.info(f"缓存中找到助手：agent_id：{agent_id}，chat_id：{chat_id}，agent：{agent}")
  return agent

# 更新助手
def delete_agent(agent_ids):
  for agent_id in agent_ids:
    agent_map[agent_id] = {}
  return agent_ids
