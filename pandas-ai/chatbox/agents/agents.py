from chatbox.output.output_element import *
from chatbox.datamanager.dataset_mamaner import DatasetManager
import pandas as pd
import re,json
import pandasai as pai
from pandasai import Agent
from pandasai.llm.base import LLM
from baml_client import b
from nicegui import run,events
import asyncio
import logging
from datetime import datetime

from pandasai.query_builders.sql_parser import SQLParser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    """用户模型"""
    def __init__(self, name: str = "用户", avatar: str = None):
        self.name = name
        self.avatar = avatar or "https://img.icons8.com/color/48/000000/user-male-circle--v1.png"
        self.current_chatbox = None
    
    async def say(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]] = None
    ):
        """用户发言"""
        if not elements:
            return
        
        if not isinstance(elements, list):
            elements = [elements]
        
        # 转换字符串为文本元素
        processed_elements = []
        for elem in elements:
            if isinstance(elem, str):
                processed_elements.append(TextElement(elem))
            elif isinstance(elem, OutputElement):
                processed_elements.append(elem)
            else:
                raise ValueError("不支持的输出元素类型")
        
        if self.current_chatbox:
            await self.current_chatbox.add_user_message(processed_elements)
        else:
            logger.warning("用户没有加入任何聊天室")  

class ChatAgent:
    """聊天智能体基类"""
    def __init__(self, name: str, role: str, llm :LLM,avatar: str = None):
        self.name = name
        self.role = role
        self.llm = llm
        self.avatar = avatar or "https://img.icons8.com/color/48/000000/robot-3.png"
        self.current_chatbox = None
        self.context = []
    
    async def say(
        self,
        elements: Union[OutputElement, str, List[Union[OutputElement, str]]] = None
    ):
        """智能体发言"""
        if not elements:
            return
        
        if not isinstance(elements, list):
            elements = [elements]
        
        # 转换字符串为文本元素
        processed_elements = []
        for elem in elements:
            if isinstance(elem, str):
                processed_elements.append(TextElement(elem))
            elif isinstance(elem, OutputElement):
                processed_elements.append(elem)
            else:
                raise ValueError("不支持的输出元素类型")
        
        if self.current_chatbox:
            await self.current_chatbox.add_agent_message(self, processed_elements)
        else:
            logger.warning(f"智能体 {self.name} 没有加入任何聊天室")
    
    async def update_msg(
        self,
        element: Union[OutputElement, str] = None,
        element_index: int = -1,
        state: str = None
    ) -> OutputElement:
        """更新消息"""
        if not element:
            return
        
        if isinstance(element, str):
            element = TextElement(element)
        
        if self.current_chatbox:
            await self.current_chatbox.update_agent_message(self, element, element_index, state)
        else:
            logger.warning(f"智能体 {self.name} 没有加入任何聊天室")
        return element
    async def insert_msg(
        self,
        element: Union[OutputElement, str]
    ) -> OutputElement:
        """插入消息"""
        if not element:
            return
        
        if isinstance(element, str):
            element = TextElement(element)
        
        if self.current_chatbox:
            await self.current_chatbox.insert_agent_message(self, element)
        else:
            logger.warning(f"智能体 {self.name} 没有加入任何聊天室")
        return element
    
    async def process_message(self, message: any, chat_context: List[Dict]):
        """处理消息（子类实现）"""
        raise NotImplementedError

class CoordinatorAgent(ChatAgent):
    """协调智能体"""
    def __init__(self,name:str=None,role:str=None, agents: List[ChatAgent]=[],*args, **kwargs):
        if name is None:
            name="协调员"        
        if role is None:
            role="协调其他智能体回答问题"
        super().__init__(name=name, role=role,*args, **kwargs)
        self.agents = {agent.name: agent for agent in agents}
    
    async def process_message(self, message: str, chat_context: List[Dict]):
        """处理消息并协调其他智能体"""
        agent_info=""
        i=0
        for agent in self.agents.values() :
            i+=1
            agent_info+=f"---Agent{i}---\n"
            agent_info+=f"Agent名字:{agent.name}\n"
            agent_info+=f"职责和技能:{agent.role}\n"

        
        # agents=b.stream.Recommendation(message,agent_info)
        
        sync_gen = b.stream.Recommendation(message, agent_info)
        async for agent in self.async_generator_wrapper(sync_gen):
            yield agent  # 转换为异步生成器
    
    async def async_generator_wrapper(self,sync_gen):
        """将同步生成器包装为异步生成器"""
        for item in sync_gen:
            yield item
            await asyncio.sleep(0)  # 让出事件循环控制权    

class DataAnalysisAgent(ChatAgent):
    """数据分析智能体"""
    def __init__(self, name:str=None,role:str=None,llm:LLM=None,correct_llm:Optional[LLM]=None,datasets:List[str]=None,*args, **kwargs):
        if llm is None:
            raise Exception("请设置智能体的LLM")
        self.correct_llm=llm if correct_llm is None else correct_llm
        role=f"""
        该Agent是一位数据分析专家，擅长多维度分析、趋势分析及数据比较，能深入挖掘数据关系，识别模式与异常，能提供清晰、可操作的洞察报告
        """ if role is None else role
        super().__init__(name=name,role=role,llm=llm,*args, **kwargs)
        self.datasets = datasets
    
    def _replace_functions(self,text:str):
        pattern = re.compile('(:\\s*)function.*?}', re.DOTALL)
        return pattern.sub("\\1''", text)
    
    async def process_message(self, message: str, chat_context: List[Dict]):
        """处理数据分析问题"""
        # 这里应该有更复杂的逻辑来解析问题和生成回答
        # 简化示例：直接返回数据集列表
        if len(self.datasets)>0:
            dfs=[]
            for dsName in self.datasets:
                dfs.append(pai.load(dsName))

            dataAgent = Agent(dfs=dfs,
                config={"llm":self.llm,"correct_llm":self.correct_llm,"verbose": True}
                ) 
            # prompt=dataAgent.generate_prompt(message)
            # pythonCode=b.stream.GenPythonCode(prompt.to_string())    
            # pythonCode = await run.io_bound(lambda: b.GenPythonCode(prompt.to_string()))
            execCode=None
            try:
                execCode = await run.io_bound(lambda: dataAgent.generate_code_with_retries(message))
            except Exception:
                yield "我不能回复你的问题"

            

            # pythonCode=b.GenPythonCode(prompt.to_string()) 
            # code =genCode()
            # execCode=pythonCode.code


                 

            if execCode is not None:
                try :
                    result = await run.io_bound(lambda: dataAgent.execute_with_retries(execCode))
                    # result=dataAgent.execute_with_retries(execCode)
                except Exception as ex:
                    result=None
                if result is not None:
                    outputEl=[]
                    for el  in result:
                        if "data" in el.keys() and el["data"] is not None and isinstance(el["data"],pd.DataFrame):
                            if len(el["data"].index) == 0: 
                                outputEl.append(MarkdownElement("很抱歉，没有查询到任何记录"))
                                continue
                            if "sql" in el.keys() and el["sql"] is not None:
                                sql_explain=""
                                if "sql_explain" in el.keys() and el["sql_explain"] is not None:
                                    sql_explain=el["sql_explain"]  
                                outputEl.append(SQLElement(sql=el["sql"],explain=sql_explain))
                                # sql=f"""
                                # {el["sql"]}
                                # """
                                # # sql=MarkdownElement(el["sql"])                              
                                # # outputEl.append(sql)                              
                                # if "sql_explain" in el.keys() and el["sql_explain"] is not None:
                                #     sql_explain=el["sql_explain"]  
                                #     sql=sql_explain+'<br>'+sql                          
                                # outputEl.append(MarkdownElement(sql))    
                                
                            explanatory=""
                            if "explanatory" in el.keys() and el["explanatory"] is not None:
                                explanatory=MarkdownElement(el["explanatory"])                              
                                # outputEl.append(explanatory)    
                            slot_info=None
                            columns_info=None

                            table_visualization_config={}
                            if "table_visualization_config" in el.keys() and el["table_visualization_config"] is not None:
                                table_visualization_config=el["table_visualization_config"]
                                
                            title=""
                            if "title" in el.keys() and el["title"] is not None:
                                title=el["title"]
                            dfEl=DataFrameElement(title=title,explanatory=explanatory,dataframe=el["data"],columns_info=columns_info,table_vis_config=table_visualization_config)
                            outputEl.append(dfEl)                        
                

                            if "analysis_info" in el.keys() and el["analysis_info"] is not None:
                                chart_config_obj=el["analysis_info"]
                                chart_config_arr=[]
                                if isinstance(chart_config_obj,dict):
                                    chart_config_arr.append(chart_config_obj)
                                else:
                                    chart_config_arr=chart_config_obj

                                for chart_config in chart_config_arr:
                                    vis_config={}
                                    if "echart_visualization_config" in el.keys():
                                        vis_config=el["echart_visualization_config"]
                                    chart=EChartElement(title=title,options=chart_config,data=el["data"],vis_config=vis_config)
                                    outputEl.append(chart)
                    yield outputEl
                else:
                    yield "我不能回复你的问题"
        else :
            yield "我不能回复你的问题"
    # 在工具类中添加
    async def async_generator_wrapper(self,sync_gen):
        for item in sync_gen:
            yield item
            await asyncio.sleep(0)  # 让出事件循环控制权

class DataAnalysisAgentMarkdown(ChatAgent):
    """数据分析智能体"""
    def __init__(self, name:str=None,role:str=None,llm:LLM=None,correct_llm:Optional[LLM]=None,datasets:List[str]=None,terms:List[Dict]=None,instructions:Dict=None,*args, **kwargs):
        if llm is None:
            raise Exception("请设置智能体的LLM")
        self.correct_llm=llm if correct_llm is None else correct_llm
        role=f"""
        该Agent是一位数据分析专家，擅长多维度分析、趋势分析及数据比较，能深入挖掘数据关系，识别模式与异常，能提供清晰、可操作的洞察报告
        """ if role is None else role
        super().__init__(name=name,role=role,llm=llm,*args, **kwargs)
        self.datasets = datasets
        # 术语配置
        self.terms = terms
        # 指令配置
        self.instructions = instructions
    
    def _replace_functions(self,text:str):
        pattern = re.compile('(:\\s*)function.*?}', re.DOTALL)
        return pattern.sub("\\1''", text)

   

    async def process_message(self, message: str, chat_context: List[Dict]):
        """处理数据分析问题"""
        # 这里应该有更复杂的逻辑来解析问题和生成回答
        # 简化示例：直接返回数据集列表
        result_json_arr=[]
        if len(self.datasets)>0:
            dfs=[]
            for dsName in self.datasets:
                dfs.append(pai.load(dsName))

            dataAgent = Agent(dfs=dfs,
                config={"llm":self.llm,"correct_llm":self.correct_llm,"verbose": True}
                ) 
            # 术语
            dataAgent._state.config.model_config["terms"] = self.terms
            # 指令
            self.instructions["CURRENT_TIME"] = f"- 当前时间是{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}，涉及到相对时间处理的请参考，譬如昨天、前天、上一天等"
            dataAgent._state.config.model_config["instructions"] = self.instructions
            result=[]
            try:
                result = await dataAgent.generate_data_with_retries(message)
                yield result
            except Exception as e:
                print(e)
                # yield "我不能回复你的问题"
                result_json_arr=[
                    {
                        "question":message,
                        "data":None,
                        "err_info":str(e)
                    }
                ]
                yield result_json_arr
                return

    # 在工具类中添加
    async def async_generator_wrapper(self,sync_gen):
        for item in sync_gen:
            yield item
            await asyncio.sleep(0)  # 让出事件循环控制权


class SocGraphExtractAgent(ChatAgent):
    """投诉工单知识图谱智能体"""
    def __init__(self, name:str=None,role:str=None,llm:LLM=None,ori_json:str=None,*args, **kwargs):
        if llm is None:
            raise Exception("请设置智能体的LLM")
        self.ori_json=ori_json
        self.current_triple=None
        role=f"""
        该Agent是一位数据分析专家，擅长多维度分析、趋势分析及数据比较，能深入挖掘数据关系，识别模式与异常，能提供清晰、可操作的洞察报告
        """ if role is None else role
        super().__init__(name=name,role=role,llm=llm,*args, **kwargs)
        
    
    def _replace_functions(self,text:str):
        pattern = re.compile('(:\\s*)function.*?}', re.DOTALL)
        return pattern.sub("\\1''", text)
    
    async def process_message(self, file_path: str, chat_context: List[Dict]):
        """处理数据分析问题"""
        if file_path is not None:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.ori_json=file.read()
            await self._handle_extract()
        else :
            yield "我不能回复你的问题"
    def _handle_conversion(self,data):
        # input_json = self.textarea.value
        # data = json.loads(input_json) 
           
        # 验证数据结构 
        if self.current_triple not in data:
            return
                # 转换数据 
        # self.echart_data = await convert_to_echarts_data(data)
        self.echart_data = self.convert_to_echarts_data_mini(data)
        if len(self.echart_data["nodes"])>0 and len(self.echart_data["links"])>0:
            if self.echart is None:
                with self.right_container:
                    print("===首次生成echart=====")
                    print(json.dumps(self.echart_data))
                    self.echart=ui.echart({
                        'tooltip': {},
                        'legend': [{
                            'data': ['指标', '时间线'],
                            'left': 'right'
                        }],
                        'series': [{
                            'type': 'graph',
                            'layout': 'force',
                            'data': self.echart_data['nodes'],
                            'links': self.echart_data['links'],
                            'categories': self.echart_data['categories'],
                            'roam': True,
                            'label': {'show': True, 'position': 'right'},
                            'draggable':True, 
                            'symbol':'roundRect',
                            'edgeLabel': {
                                'show': True,
                                'formatter': '；{@name}',
                                'color': '#666'
                            },
                            'force': {
                                'repulsion': 500,
                                'edgeLength': 100
                            },
                            'labelLayout': {
                                'hideOverlap': False
                            },
                            'lineStyle': {
                                'color': 'source',
                                'curveness': 0.1
                            }
                        }]
                    } ).classes("w-full h-full p-4") 
                    print("===首次生成echart 结束=====")
            else: 
                print("===继续更新echart=====")
                options=self.echart.options
                options['series'][0]['data']=self.echart_data['nodes']
                options['series'][0]['links']=self.echart_data['links']
                self.echart.run_chart_method('setOption',options)
                # await run.io_bound(lambda: self._wrap_echart_setOption(options))

    def _wrap_echart_setOption(self,options):
        self.echart.run_chart_method('setOption',options)

    def _handle_upload(self, e: events.UploadEventArguments):
        """处理文件上传"""
        try:
            file_content = e.content.read().decode('utf-8')  # 读取文件内容并解码为字符串
            #保存需要抽取的json
            self.orijson=file_content
            ui.notify(f"上传成功") 
        except Exception as ex:

            ui.notify(f"上传失败: {str(ex)}", type='negative')     
    async def _handle_extract(self):
        """处理文件上传"""
        # try:
        # sync_gen=b.stream.GenTask(self.orijson)
        print("=======开始抽取===========")
        asyncio.create_task(self.process_agent_reply())
         
    async def process_agent_reply(self):

        # self.textarea.value=json.dumps(gen)
        await asyncio.sleep(0.01) 
        sync_gen=self._generator(self.orijson)
        preCount=0
        async for jsonGen in sync_gen:
            # strJson=str(json)
            # print(strJson)
            strJson=jsonGen.model_dump_json(indent=4)
            # self.textarea.value=strJson
            jsonObj=jsonGen.model_dump() 
            #如果新增1个节点就更新图
            if self.current_triple in jsonObj:
                if len(jsonObj[self.current_triple])>preCount:
                    print(f"=======渲染图谱===={preCount}")
                    preCount=len(jsonObj[self.current_triple])   
                    # asyncio.sleep(0.02)                 
                    self._handle_conversion(jsonObj) 
          

    async def _generator(self,orijson:str):
        # sgen=b.stream.GenEventKS(self.orijson) 
        # sgen=b.stream.GenEventSB(self.orijson) 
        # sgen=b.stream.GenEventTY(self.orijson)  
        # sgen=b.stream.GenIndexGL(self.orijson) 
        # sgen=b.stream.GenIndexNU(self.orijson) 
        # synsgenc_gen=b.stream.GenIndexCE(self.orijson)
        # sgen=b.stream.GenIndexYW(self.orijson)        
        sgen=b.stream.GenIndexZD(orijson)
        async for jGen in self._async_generator_wrapper(sgen):
            yield jGen
         

    async def _async_generator_wrapper(self,sync_gen):
        """将同步生成器包装为异步生成器"""
        for item in sync_gen:
            yield item
            await asyncio.sleep(0)  # 让出事件循环控制权 
        # except Exception as ex:

            # ui.notify(f"抽取失败: {str(ex)}", type='negative') 
    def convert_to_echarts_data_mini(self,input_data):
        nodes = []
        links = []
        existing_nodes = set()

        # 定义节点类别样式
        categories = [{'name': 'head'}, {'name': 'tail'}]
        tail_id_num=0
        if self.current_triple in input_data and (self.current_triple=='netEventAndLocationTriple' or self.current_triple=='eventTyTriples'):
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'tc': triple['r']['tc'],
                    'ec': triple['r']['ec'],
                    'ct': triple['r']['ct']
                })
        elif self.current_triple in input_data and self.current_triple=='eventFailTriples':
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'tc': triple['r']['tc'],
                    'ec': triple['r']['ec'],
                    'ct': triple['r']['ct']
                })   

        elif self.current_triple in input_data and self.current_triple=='indexOverviewTriple':
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'v': triple['r']['v']
                })       
        elif self.current_triple in input_data and self.current_triple=='indexNetUnitTriples':
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'v': triple['r']['v'],
                    'j': triple['r']['j'],
                    'z': triple['r']['z'],
                    'm': triple['r']['m']
                })    
        elif self.current_triple in input_data and self.current_triple=='indexCellTriples':
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'v': triple['r']['v'],
                    'j': triple['r']['j'],
                    'z': triple['r']['z'],
                    'm': triple['r']['m']
                })                  
        elif self.current_triple in input_data and self.current_triple=='indexBusinessTriples':
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'v': triple['r']['v'],
                    'j': triple['r']['j'],
                    'z': triple['r']['z'],
                    'm': triple['r']['m']
                }) 
        elif self.self.current_triple in input_data and self.current_triple=='indexTerminalTriples':
            for triple in input_data[self.current_triple]:
                # 处理head节点
                head = triple['h']
                tail = triple['t']
                if head is None or tail is None:
                    continue

                head_id = f"head_{head['tp']}_{head['n']}"
                if head_id not in existing_nodes:
                    nodes.append({
                        'id': head_id,
                        'name': head['n'],
                        'category': 0,  # 对应categories中的head
                        'symbolSize': 30,
                        'itemStyle': {'color': '#4f19c7'}
                    })
                    existing_nodes.add(head_id)

                # 处理tail节点
                tail_id_num+=1
                tail_id = f"tail_{tail['n']}"
                if tail_id not in existing_nodes:
                    nodes.append({
                        'id': tail_id,
                        'name': f"{tail['n']}",
                        'category': 1,  # 对应categories中的tail
                        'symbolSize': 20,
                        'itemStyle': {'color': '#19c775'}
                    })
                    existing_nodes.add(tail_id)
    
                # 添加关系
                links.append({
                    'source': head_id,
                    'target': tail_id,
                    'name': triple['r']['n'],
                    'v': triple['r']['v'],
                    'j': triple['r']['j'],
                    'z': triple['r']['z'],
                    'm': triple['r']['m']
                }) 

        return {
            'nodes': nodes,
            'links': links,
            'categories': categories
        }


def genCode():
    yield "aaaaaaaaaaaaaaa"
    yield "aaaaaaaaaaaaaaabbbbbbbbbbbbbbbb"      
    yield "aaaaaaaaaaaaaaabbbbbbbbbbbbbbbbcccccccccccccccccccccccc"    
    yield "aaaaaaaaaaaaaaabbbbbbbbbbbbbbbbcccccccccccccccccccccccceeeeeeeeeeeeeeeeeee" 
    yield "aaaaaaaaaaaaaaabbbbbbbbbbbbbbbbcccccccccccccccccccccccceeeeeeeeeeeeeeeeeeefffffffffffffffffffffffffff" 
    yield "aaaaaaaaaaaaaaabbbbbbbbbbbbbbbbcccccccccccccccccccccccceeeeeeeeeeeeeeeeeeefffffffffffffffffffffffffffggggggggggggggggggggg"   

class GeneralChatAgent(ChatAgent):
    """通用聊天智能体"""
    def __init__(self,*args, **kwargs):
        super().__init__(name="助手", role="当其他agent不能不能处理问题时，交给它做一般性的回答",*args, **kwargs)
    
    def process_message(self, message: str, chat_context: List[Dict]):
        """处理一般性问题"""
        # 这里应该有更复杂的逻辑来生成回答
        # 简化示例：返回简单回复
        result= [TextElement(f"你好！我是一个通用助手。你问的是: {message}")]
        yield result

        