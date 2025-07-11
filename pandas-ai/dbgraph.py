from nicegui import ui
from trino.dbapi import connect
from typing import Dict, List, Optional, Tuple
import json

from whyhow import WhyHow
from whyhow import Chunk, Triple, Node, Relation
import os
os.environ['WHYHOW_API_KEY']='aaa'
categories=[{'name': '表','symbol':'circle','symbolSize':30} 
            , {'name': '列','symbol':'rect','symbolSize':30}
            ]
class TrinoSchemaToGraph:
    def __init__(self, host: str, port: int, user: str, catalog: str, schema: str):
        """
        初始化Trino数据库连接
        
        :param host: Trino服务器地址
        :param port: Trino端口(默认8080)
        :param user: 用户名
        :param catalog: 目录名(如hive)
        :param schema: 模式名(如default)
        """
        self.conn = connect(
            host=host,
            port=port,
            user=user,
            catalog=catalog,
            schema=schema
        )
        self.cursor = self.conn.cursor()
        self.catalog = catalog
        self.schema = schema

    def _execute_query(self, query: str) -> List[Tuple]:
        """执行SQL查询并返回结果"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_tables_with_columns(self) -> Dict[str, Dict]:
        """
        获取所有表及其列信息（单次查询优化）
        
        :return: {
            "table1": {
                "comment": "表注释",
                "columns": [
                    {"name": "col1", "type": "varchar", "comment": "列注释"},
                    ...
                ]
            },
            ...
        }
        """
        tables = {}
        
        # 获取所有表名
        tables_query = f"SHOW TABLES FROM {self.catalog}.{self.schema}"
        table_names = [row[0] for row in self._execute_query(tables_query)]
        i=0
        for table_name in table_names:
            if i==1:
                break
            # 获取表结构和注释
            desc_query = f"DESCRIBE {self.catalog}.{self.schema}.{table_name}"
            desc_rows = self._execute_query(desc_query)
            
            table_comment = ""
            columns = []
            
            # 解析DESCRIBE结果
            for row in desc_rows:
                # 表注释行通常格式为 ('Comment', '注释内容', '', '')
                if len(row) >= 2 and row[0] == "Comment":
                    table_comment = row[1]
                # 列信息行通常格式为 (列名, 类型, '', 注释)
                elif len(row) >= 4 and row[0] != "Comment":
                    columns.append({
                        "name": row[0],
                        "type": row[1],
                        "comment": row[3] if len(row) > 3 else ""
                    })
            
            tables[table_name] = {
                "comment": table_comment,
                "columns": columns
            }
            i+=1
        
        return tables

    def generate_graph(self) -> Dict:
        """
        生成图数据结构
        
        :return: {
            "nodes": [
                {"id": "table1", "type": "table", "label": "table1", "comment": "..."},
                {"id": "table1.col1", "type": "column", "label": "col1", ...},
                ...
            ],
            "edges": [
                {"source": "table1", "target": "table1.col1", "relationship": "contains"},
                ...
            ]
        }
        """
        graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "catalog": self.catalog,
                "schema": self.schema,
                "graph_type": "table-column-relationship"
            }
        }
        
        tables_data = self.get_tables_with_columns()
        
        for table_name, table_info in tables_data.items():
            # 添加表节点
         
            table_node = {
                "id": table_name,
                "type": "table",
                "label": table_name,
                "name":table_name,
                "comment": table_info["comment"],
                "catalog": self.catalog,
                "category":0,
                "schema": self.schema
            }
            graph["nodes"].append(table_node)
            
            # 添加列节点和关系边
            for col in table_info["columns"]:
                col_id = f"{table_name}.{col['name']}"
                col_name=col["name"]
                if str.strip(col["comment"])!='':
                    col_name+='['+col["comment"]+']'
                    
                col_node = {
                    "id": col_id,
                    "type": "column",
                    "label": col["name"],
                    "name": col_name,
                    "data_type": col["type"],
                    "comment": col["comment"],
                    "parent_table": table_name,
                    "category":1
                }
                graph["nodes"].append(col_node)
                
                # 添加表-列关系边
                edge = {
                    "source": table_name,
                    "target": col_id,
                    "relationship": "contains",
                    "type": "table-column"
                }
                graph["edges"].append(edge)
        
        return graph

    def save_graph_to_file(self, file_path: str, indent: Optional[int] = 2):
        """
        将图数据保存到JSON文件
        
        :param file_path: 文件路径
        :param indent: JSON缩进(None表示不缩进)
        """
        graph_data = self.generate_graph()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=indent, ensure_ascii=False)

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()



# 创建Trino配置界面
with ui.card().classes('w-full'):
    ui.label('Trino配置').classes('text-2xl')
    host = ui.input('Trino服务地址', value='localhost').props('outline')
    port = ui.input('端口', value='18080').props('outline')
    user = ui.input('用户名', value='trino').props('outline')
    catalog = ui.input('Catalog', value='mysql').props('outline')
    schema = ui.input('Schema', value='bikestores').props('outline')

chart =None
client =None
workspace=None
trino_graph=None
async def generate_graph():
    global chart
    global workspace
    global client
    global trino_graph
    config = {
        'host': host.value,
        'port': port.value,
        'user': user.value,
        'catalog': catalog.value,
        'schema': schema.value
    }
    if client is None:
        client = WhyHow(api_key='dli3TwaLmQoCXNhioWF93a49zPxrDniSFwocbQnL',base_url="http://127.0.0.1:8000")
        workspace=client.workspaces.get('6810f9b6c7446944bc771ee1')
        if workspace is None:
            workspace = client.workspaces.create(name="dbgraph")
    if trino_graph is None:
        trino_graph = TrinoSchemaToGraph(**config) 
    data = trino_graph.generate_graph()
    # 将所有node放到map
    node_map = {item['id']: item for item in data['nodes']}
    # 转换为图数据
    triples = []
    for link in data['edges']:
        sid=link['source']
        tid=link['target']
        snode=node_map[sid] 
        tnode=node_map[tid]
        # uploaded_chunk = client.chunks.create(workspace_id=workspace.workspace_id, chunks=[Chunk(content=chunk)])
        # triple = Triple(
        #     head=Node(name=snode['name'], label=snode['label']),
        #     relation=Relation(name="包含"),
        #     tail=Node(name=tnode['name'], label=tnode['label']),
        #     # chunks=[uploaded_chunk[0].chunk_id]
        # )
        client.triples.create(
            graph_id='6810fd08c7446944bc771ee5',
            head=Node(name=snode['name'], label=snode['label'],properties={}),
            relation=Relation(name="包含"),
            tail=Node(name=tnode['name'], label=tnode['label'],properties={}),
            strict_mode=True,
            properties={},
            chunks=[]

        )
        # triples.append(triple)

    # graph = client.graphs.create_graph_from_triples(
    #     workspace_id=workspace.workspace_id,
    #     triples=triples,
    #     name="数据库图"  
    # )
    print(data)
    if data:
        ops={
                'tooltip': {},
                'legend': [{
                    'data': [el['name']  for el in categories ],
                    'left': 'left'
                }],
                'toolbox': {
                    'show': True,
                    'feature': {
                        'dataView': { 'readOnly': False },
                        'restore': {},
                        'saveAsImage': {}
                    }
                },               
                'series': [{
                    'type': 'graph',
                    'layout': 'force',
                    'data': data['nodes'],
                    'links': data['edges'],
                    'categories':categories,
                    'roam': True,
                    'label': {'show': True, 'position': 'top'},
                    'draggable':True, 
                    'edgeSymbol': ['none', 'arrow'],
                    'edgeSymbolSize': [0, 8],
                    'force': {
                        'repulsion': 500,
                        'edgeLength': 100
                    },
                    'labelLayout': {
                        'hideOverlap': False
                    },
                    'lineStyle': {
                        'width':2,
                        'color': 'source', 
                        'curveness': 0.1
                    }
                }]
            }
        if chart is None:
            with chart_card:
                chart=ui.echart(ops).classes('w-full h-96')    
        else:
            chart.run_chart_method('setOption',ops)

        


ui.button('生成图谱', on_click=generate_graph).props('outline')
chart_card=ui.card().classes('w-full')

ui.run(title='数据库结构可视化(Trino版)', reload=True)