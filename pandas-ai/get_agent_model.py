# pip install mysql-connector-python==8.0.23
import mysql.connector
import json
from collections import defaultdict

# 从 库名.表名 的格式种提取表名
def extractTableName(fullName):
    if "." in fullName:
        return fullName.split('.')[-1]
    else:
        return fullName

# 字段类型映射
def typeMapping(originType):
    originTypeLower = originType.lower()
    if "int" in originTypeLower:
        return "integer"
    elif "date" in originTypeLower or "time" in originTypeLower:
        return "datetime"
    elif "char" in originTypeLower or "text" in originTypeLower or "lob" in originTypeLower or "json" in originTypeLower or "xml" in originTypeLower:
        return "string"
    elif "float" in originTypeLower or "double" in originTypeLower or "dec" in originTypeLower or "numeric" in originTypeLower or "number" in originTypeLower:
        return "float"
    elif "bool" in originTypeLower:
        return "boolean"
    else:
        return originType

def parseDimension(modelDimensionRows, fieldsDict):
    columns = []
    if len(modelDimensionRows) > 0:
        for dimensionRow in modelDimensionRows:
            column = {
                "name": dimensionRow.get("expr", ""),
                "alias": dimensionRow.get("name", ""),
                "description": dimensionRow.get("description", "")
            }
            if dimensionRow.get("expr", "") == dimensionRow.get("biz_name", "1"):
                column["expr"] = 0
                column["type"] = typeMapping(fieldsDict.get(column["name"].lower(), {}).get("dataType", ""))
            else:
                column["expr"] = 1
                column["type"] = ""
            columns.append(column)
    return columns

def parseMetric(modelMetricRows, fieldsDict):
    columns = []
    if len(modelMetricRows) > 0:
        for metricRow in modelMetricRows:
            column = {
                "name": json.loads(metricRow.get("type_params", "{}")).get("expr", ""),
                "alias": metricRow.get("name", ""),
                "description": metricRow.get("description", "")
            }
            defineType = metricRow.get("define_type", "")
            if "METRIC" == defineType or "FIELD" == defineType:
                column["expr"] = 1
                column["type"] = ""
            elif "MEASURE" == defineType:
                column["expr"] = 0
                column["type"] = typeMapping(fieldsDict.get(column["name"].lower(), {}).get("dataType", ""))
            else:
                column["expr"] = 0
                column["type"] = ""
            columns.append(column)
    return columns


#     将一维数组切分为二维数组，每行 chunk_size 个元素
#
#     arr: 输入的一维列表或数组
#     chunk_size: 每行元素数量，默认为 100
#     返回二维列表
def split_array(arr, chunk_size=100):
    return [arr[i:i+chunk_size] for i in range(0, len(arr), chunk_size)]

# 执行sql
def executeSqlIn(cursor, sql, inColumnName, inParams):
    finalSql = sql
    if len(inParams) > 0:
        placeholders = ', '.join(['%s'] * len(inParams))
        if "where" in sql.lower():
            finalSql = f"{sql} and {inColumnName} in ({placeholders})"
        else:
            finalSql = f"{sql} where {inColumnName} in ({placeholders})"
    print(f"执行sql: {finalSql}")
    cursor.execute(finalSql, tuple(inParams))
    return cursor.fetchall()

def getAgentModels(host, port, user, password, database, agentIds=[]):
    print(f"连接数据库: {host}、 {port}、 {user}、 {password}、 {database}、 助理ID：{agentIds}")
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            auth_plugin='mysql_native_password'  # 解决认证协议问题 :ml-citation{ref="5" data="citationList"}
        )
        cursor = conn.cursor(dictionary=True)

        result = []

        # 查询助理信息后遍历
        agentRows = executeSqlIn(cursor, "select id, name, description, tool_config from s2_agent", "id", agentIds)
        if len(agentRows) <= 0:
            print("没有找到助理")
            return result
        for agentRow in agentRows:
            print(f"id:{agentRow['id']}\t name:{agentRow['name']}\t description:{agentRow['description']}")
            toolConfig = json.loads(agentRow.get("tool_config", "{}"))
            dataSetIds = set()
            # 获取某个助手的数据集ID
            for tool in toolConfig.get("tools", []):
                if "DATASET" == tool.get("type", ""):
                    dataSetIds.update(tool.get("dataSetIds",[]))
            print(f"dataSetIds:{dataSetIds}")

            if len(dataSetIds) <= 0:
                continue
            # 根据数据集ID获取模型ID
            dataSetRows = executeSqlIn(cursor, "select data_set_detail from s2_data_set", "id", dataSetIds)

            modelIds = set()
            for dataSetRow in dataSetRows:
#                 print(dataSetRow)
                dataSetDetail = json.loads(dataSetRow.get("data_set_detail", "{}"))
                modelIds.update([item["id"] for item in dataSetDetail.get("dataSetModelConfigs", [])])
            print(f"modelIds:{modelIds}")
            if len(modelIds) <= 0:
                continue

            # 根据模型ID，获取模型信息
            models = []

            # 每次查100个模型，防止超过 IN 参数限制
            for partModelIds in split_array(sorted(modelIds)):
                # 查询模型表
                modelRows = executeSqlIn(cursor, "select id, description, model_detail from s2_model", "id", partModelIds)

                # 查询维度字段表
                modelDimensionRows = executeSqlIn(cursor, "select model_id, expr, name, biz_name, description from s2_dimension", "model_id", partModelIds)
                modelDimensionRowsDict = defaultdict(list)
                for dimensionRow in modelDimensionRows:
                    modelDimensionRowsDict[dimensionRow.get("model_id", "")].append(dimensionRow)

                # 查询度量字段表
                modelMetricRows = executeSqlIn(cursor, "select model_id, define_type, type_params, name, description from s2_metric", "model_id", partModelIds)
                modelMetricRowsDict = defaultdict(list)
                for metricRow in modelMetricRows:
                    modelMetricRowsDict[metricRow.get("model_id", "")].append(metricRow)

                for modelRow in modelRows:
                    # 封装模型信息
                    model = {}
                    model["description"] = modelRow.get("description", "")
                    modelColumns = []
                    modelDetails = json.loads(modelRow.get("model_detail", "{}"))
                    if "table_query" == modelDetails.get("queryType", "").lower():
                        model["table_name"] = extractTableName(modelDetails.get("tableQuery", "").lower())
                    else:
                        model["table_name"] = ""

                    # 封装字段信息
                    fieldsDict = {field.get("fieldName", "").lower(): field for field in modelDetails.get("fields", [])}
                    modelColumns.extend(parseDimension(modelDimensionRowsDict.get(modelRow["id"], []), fieldsDict))
                    modelColumns.extend(parseMetric(modelMetricRowsDict.get(modelRow["id"], []), fieldsDict))
                    model["columns"] = modelColumns

                    models.append(model)

            # 封装助理信息
            result.append({
                "id": agentRow['id'],
                "name": agentRow['name'],
                "description": agentRow['description'],
                "models": models
            })
        return result
    except Exception as e:
        print(f"数据库操作失败: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("数据库连接已关闭")

# 转换结果写入文件
def writeJsonFile(result):
#     print(f"result: {result}")
    with open("agentModels.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


result = getAgentModels("192.168.108.63", 3306, "root", "Hantele@2023!", "supersonic", agentIds=[])
writeJsonFile(result)