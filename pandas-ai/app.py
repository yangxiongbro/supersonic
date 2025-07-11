"""
多智能体协作聊天系统
功能：类似微信的群聊效果，用户和多个智能体在一个聊天窗口进行交流互动
包含：数据库管理、数据集管理、多模态输出、智能体协作等功能
"""

import os
import shutil
import time
import logging
from typing import List, Union, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import pandasai as pai
import duckdb
from nicegui import ui, app, events
from nicegui import run
from nicegui.elements.spinner import SpinnerTypes
from nicegui.elements.scene_objects import Object3D
import io
import base64
import hashlib
import yaml
from enum import Enum, auto
# from nicegui_toolkit import inject_layout_tool
from pandasai.helpers.path import (
    find_dataset_base_path
)
from pandasai.core.prompts import (
    get_chat_prompt_for_sql,
    get_correct_error_prompt_for_sql,
    get_correct_output_type_error_prompt,
    get_analyze_report_prompt
)
from pandasai.dataframe import DataFrame, VirtualDataFrame
from pandasai.llm.base import LLM
from pandasai import Agent
from extensions.llms.openai.pandasai_openai import OpenAI

from baml_client import b
from baml_client.types import Agents
import asyncio
import json
from chatbox.output.visrender.vis_render import *

from chatbox.output.output_element import *
from chatbox.datamanager.dataset_mamaner import DatasetManager
from chatbox.datamanager.dbmanager import DatabaseManager
from chatbox.agents.agents import *
from chatbox.agents.ragflow_agent import *
from chatbox.chatbox import ChatBox
from fastapi import Request
from sync_data.sync_agent import get_agent_infos
from common.http_response import HttpResponse

# inject_layout_tool()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OpenAI._supported_chat_models.append("deepseek-v3-250324")
OpenAI._supported_chat_models.append("deepseek-ai/DeepSeek-V3")
# dsv3 = OpenAI(max_tokens=8192,temperature=0,model="deepseek-chat",api_token="sk-88e439451b974cf2b4e74dd58a904f8e",api_base="https://api.deepseek.com/v1")
dsv3 = OpenAI(max_tokens=8192,temperature=0,model="deepseek-ai/DeepSeek-V3",api_token="sk-yfibapxotobrduqertxcvhpjykczzjikeekxcrrgsqspggkd",api_base="https://api.siliconflow.cn/v1")
# qwen = OpenAI(max_tokens=8192,temperature=0,model="qwen2.5-coder-32b-instruct",api_token="sk-8cab883d8d964e0281cf774a552f98b4",api_base="https://dashscope.aliyuncs.com/compatible-mode/v1")
# dsv3 = OpenAI(max_tokens=8192,temperature=0,model="deepseek-v3-241226",api_token="8e8723a1-8032-4213-9752-748fbd9fbd70",api_base="https://ark.cn-beijing.volces.com/api/v1")
# dsv3 = OpenAI(max_tokens=8192,temperature=0,model="""deepseek-ai/DeepSeek-V3""",api_token="sk-dkihzhdvaowvyastvjtnhutiyyfrsntqnptbpehuvbhfytzz",api_base="https://api.siliconflow.cn/v1")
# pai.config.set("temperature", 0)
# llm = OpenAI(
#     model="deepseek-r1-distill-qwen-32b-250120",
#     api_token="8e8723a1-8032-4213-9752-748fbd9fbd70",
#     api_base="https://ark.cn-beijing.volces.com/api/v1",
#     max_tokens=8192,
#     temperature=0
    
#     )


# ====================== 界面布局 ======================
app.add_static_files('/static', 'static')

class MultiAgentChatApp:
    """多智能体聊天应用"""
    def __init__(self):
        # 初始化管理器
        self.db_manager = DatabaseManager()
        self.dataset_manager = DatasetManager(self.db_manager)
        
        # 创建用户
        self.user = User()        
        # 创建智能体
        # role1="""
        # 该Agent是一位项目缺陷数据分析专家，擅长通过研发项目所记录的缺陷清单分析项目的质量情况，它可以将数据生成表格和绘制图表，
        # 它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
        # """
        # bug_agent = DataAnalysisAgent(name="缺陷分析助手",role=role1,llm=dsv3,correct_llm=dsv3,datasets=['myorg/abug'],avatar="https://cdn.quasar.dev/img/avatar4.jpg")
        # role2="""
        # 该Agent是一位自行车销售数据分析专家，它掌握以下数据：
        # 1、自行车产品信息，可随时提供产品的详细信息
        # 2、客户信息，可提供客户的详细信息
        # 3、订单和订单详情
        # 4、门店信息，可提供售卖自行车产品的门店详细信息
        # 5、职员信息，可提供各门店职员的详细信息
        # 基于以上数据，可以将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
        # """
        # product_agent = DataAnalysisAgent(name="自行车销售分析助手",role=role2,llm=dsv3,correct_llm=dsv3,datasets=
        #                                 ['myorg/trino-mysql-brands','myorg/trino-mysql-categories',
        #                                  'myorg/trino-mysql-order','myorg/trino-mysql-order-items',
        #                                  'myorg/trino-mysql-store','myorg/trnio-mysql-products','myorg/trino-mysql-staffs',
        #                                  ],avatar="https://cdn.quasar.dev/img/avatar4.jpg")

 
        # # role="""
        # # 该Agent是一位企业员工信息分析专家，它可以帮你获取员工的详细信息，包括工号、姓名、部门、业务线条、工作组
        # # """
        # # renyuan_agent = DataAnalysisAgent("员工信息助手",role,['myorg/renyuan'],llm=llm,avatar="https://cdn.quasar.dev/img/avatar4.jpg")        
        # general_agent = GeneralChatAgent(llm=dsv3,avatar="https://cdn.quasar.dev/img/avatar5.jpg")

        # role3='''
        # 该agent是研发知识库助手，它具备以下知识：
        # 1、python、java相关技术
        # 2、研发流程相关知识
        # 3、IT技术
        # '''
        # ragflow_agent=RagflowAgent(name='研发知识助手',role=role3,api_host='http://192.168.16.22:8080',api_key='ragflow-MwMDI2MWJhMWVjOTExZjBiNDFkMDI0Mm',agent_id='bbd62fa61ec811f08aa40242ac190006')

        # role4="""
        # 该Agent是一位一线和二线投诉工单基础信息分析专家，它掌握数据集包含：
        # 1、一线投诉工单基础信息：该数据集包含工单创建时间、省份、业务、服务请求分类1、服务请求分类2、服务请求分类3、服务请求分类4、服务请求分类5、一线客服流水、二线工单号、二线工单内容、省份或二线、全球通身份等级、用户星级、在统一客服系统停留时长、在集中客服团队停留时长、是否满意、紧急程度、用户姓名、手机号码、工单归档时间、24小时口径处理时长、互联网侧时长、首回复时长、是否24小时超时、是否分层分级超时、是否首回复16小时超时等信息。其中维度为工单创建时间、省份、业务、服务请求分类1、服务请求分类2、服务请求分类3、服务请求分类4、服务请求分类5、一线客服流水、二线工单号、省份或二线、全球通身份等级、用户星级、工单归档时间，指标为二线工单内容、24小时口径处理时长、互联网侧时长、首回复时长、是否24小时超时、是否分层分级超时、是否首回复16小时超时
        # 2、二线投诉工单基础信息：该数据集包含了一线投诉工单的明细数据，可以查询一线投诉工单的数量，创建时间，工单内容，处理内容等
        # 基于以上数据，可以通过多维度分析二线投诉工单数据，并将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
        # """
        # yx_agent = DataAnalysisAgent(name="投诉工单基础信息分析助手",role=role4,llm=dsv3,correct_llm=dsv3,datasets=
        #                                 ['myorg/trino-dy-n1-tp-0005-base-count-byd','myorg/trino-dy-second-workorder-detail'
        #                                  ],avatar="https://cdn.quasar.dev/img/avatar4.jpg")
        
        # role5="""
        # 该Agent善于分析中国移动互联网的业务产品(简称互联网产品)在各季度的用户体验满意度评分数据，它可以：
        # 1、获取中国移动集团(简称集团)调研满意度调研的产品
        # 2、分析互联网产品在各季度的满意度得分情况
        # 基于以上数据，可以将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
        # """
        # kqi_agent = DataAnalysisAgent(name="互联网产品满意度分析助手",role=role5,llm=dsv3,correct_llm=dsv3,datasets=
        #                                 ['myorg/trino-dy-jiuan-manyidu-byq',
        #                                  ],avatar="https://cdn.quasar.dev/img/avatar4.jpg")        

        # role6="""
        # 该Agent善于分析中国移动互联网的用户信息(简称互联网用户)在各季度的用户体验满意度评分数据，它可以：
        # 1、获取用户模型
        # 2、分析用户模型
        # 基于以上数据，可以将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
        # """
        # user_agent = DataAnalysisAgent(name="互联网用户分析助手",role=role6,llm=dsv3,correct_llm=dsv3,datasets=
        #                                 [
        #                                  ],avatar="https://cdn.quasar.dev/img/avatar4.jpg")       

        # coordinator_agent = CoordinatorAgent(agents=[bug_agent,product_agent,kqi_agent,yx_agent,ragflow_agent,user_agent],llm=dsv3,avatar="https://cdn.quasar.dev/img/avatar3.jpg")
        
        coordinator_agent = CoordinatorAgent(agents=[],llm=dsv3,avatar="https://cdn.quasar.dev/img/avatar3.jpg")

        # 创建聊天室
        self.chat_box = ChatBox(self.user,coordinator_agent)
        
        # 当前选中的数据集
        self.current_dataset = None
        
        # 初始化UI
        self.init_ui()
   

    def init_ui(self):
        """初始化用户界面"""
        # 添加CSS样式
        ui.add_head_html('''
            <style>
                html, body {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden; /* 禁用窗口滚动条 */
                }
                      
                /* 固定布局样式 */
                .splitter-panel {
                    flex: 0 0 auto !important;
                    overflow: hidden !important;
                }
                
                
                /* 滚动条样式 */
                ::-webkit-scrollbar {
                    height: 8px;
                    width: 8px;
                }
                /* 滚动条轨道 */
                ::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                } 
                /* 滚动条滑块 */
                ::-webkit-scrollbar-thumb {
                    background: #c1c1c1;
                    border-radius: 4px;
                }   
                /* 鼠标悬停时的滑块 */
                ::-webkit-scrollbar-thumb:hover {
                    background: #a8a8a8;
                }
                .q-scrollarea__content {
                    max-width:100%
                }
                                              
            </style>
        ''')
         
        # 主布局 - 固定分割比例
        with ui.splitter(value=50).classes("w-full h-[calc(100vh-16px)]") as splitter:
            with splitter.before:
                self._init_left_panel()
            with splitter.after:
                self._init_right_panel()    
    
    
    
    def _init_left_panel(self):
        """初始化左侧面板（数据集管理）"""
        with ui.column().classes("w-full h-full p-4 overflow-y-scroll overflow-x-hidden"):
            ui.label("数据集管理").classes('text-xl font-bold mb-4')
            
            # 上传区域
            with ui.card().classes('w-full p-4 mb-4'):
                ui.label("上传新数据集").classes('font-bold mb-2')
                self.upload = ui.upload(
                    label="选择CSV文件",
                    on_upload=lambda e: self.handle_upload(e),
                    auto_upload=True
                ).classes('w-full')
                self.upload.props('accept=.csv')
            
            # 数据集列表
            with ui.card().classes('w-full p-4'):
                ui.label("数据集列表").classes('font-bold mb-2')
                self.dataset_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': '名称', 'field': 'name', 'sortable': True},
                        {'name': 'size', 'label': '大小', 'field': 'size', 'sortable': True},
                        {'name': 'created_at', 'label': '创建时间', 'field': 'created_at', 'sortable': True}
                    ],
                    rows=[],
                    row_key='name',
                    selection='single',
                    on_select=lambda e: self.handle_dataset_select(e)
                ).classes('w-full max-h-64')
                
                
                # 操作按钮
                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button('刷新', on_click=self.refresh_datasets).classes('mr-2')
                    ui.button('删除', on_click=self.delete_selected_dataset, color='negative')
            self.refresh_datasets()
            
            # 数据集预览
            with ui.card().classes('w-full p-4 overflow-hidden'):
                ui.label("数据集预览").classes('font-bold mb-2')
                with ui.scroll_area().classes('w-full max-h-96'):
                    self.preview_table = ui.table(
                        columns=[],
                        rows=[],
                        row_key='id',
                        pagination=10
                    ).classes("w-full max-h-200 overflow-auto").props('dense flat bordered')   
                 

    def _init_right_panel(self):
        """初始化右侧面板（聊天区域）"""
        with ui.column().classes("w-full h-full p-4"):
            ui.label("多智能体协作聊天").classes('text-xl font-bold mb-4')
            
            # 聊天消息容器
            with ui.scroll_area().classes('w-full flex-grow message-container') as scroll:
                self.chat_box.chat_container = scroll
            
            # 输入区域
            with ui.column().classes('w-full mt-4'):
                with ui.row().classes('w-full items-center'):
                    self.message_input = ui.textarea(
                        placeholder='输入消息...',
                        on_change=self.handle_keydown
                    ).classes('w-full').props('autofocus outlined')
                
                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button('发送', on_click=self.send_message, icon='send').classes('mr-2')
                    ui.button('清空', on_click=self.clear_input, color='negative')
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def refresh_datasets(self):
        """刷新数据集列表"""
        self.dataset_manager.load_datasets()
        datasets = self.dataset_manager.get_dataset_list()
        rows = []
        for dataset in datasets:
            rows.append({
                'name': dataset['name'],
                'size': self.format_size(dataset['size']),
                'created_at': dataset['created_at'].strftime('%Y-%m-%d %H:%M')
            })
        self.dataset_table.rows = rows
        self.dataset_table.update()
    
    def handle_upload(self, e: events.UploadEventArguments):
        """处理文件上传"""
        try:
            # 保存临时文件
            file_path = f"temp_{e.name}"
            with open(file_path, 'wb') as f:
                f.write(e.content.read())
            
            # 创建数据集
            dataset_name = self.dataset_manager.create_dataset(file_path)
            
            # 删除临时文件
            os.remove(file_path)
            
            # 刷新列表
            self.refresh_datasets()
            
            ui.notify(f"数据集 {dataset_name} 上传成功", type='positive')
        except Exception as ex:
            logger.error(f"上传失败: {ex}")
            ui.notify(f"上传失败: {str(ex)}", type='negative')
    

    def handle_dataset_select(self, e: events.GenericEventArguments):
        """处理数据集选择"""
        if not e.selection or len(e.selection) == 0:
            return
        
        # 获取第一个选中项（假设单选模式）
        selected_item = e.selection[0]
        
        # 确保我们获取的是字典且有name字段
        if isinstance(selected_item, dict) and 'name' in selected_item:
            dataset_name = selected_item['name']
            self.current_dataset = dataset_name
            
            try:
                # 获取预览数据
                preview_df = self.dataset_manager.get_dataset_preview(dataset_name)
                
                # 更新预览表格
                self.preview_table.columns = [
                    {'name': col, 'label': col, 'field': col} 
                    for col in preview_df.columns
                ]
                self.preview_table.rows = preview_df.to_dict('records')
                self.preview_table.update()
                
                ui.notify(f"已加载数据集: {dataset_name}", type='positive')
            except Exception as ex:
                logger.error(f"加载数据集失败: {ex}")
                ui.notify(f"加载数据集失败: {str(ex)}", type='negative')
        else:
            logger.error(f"无效的选择项格式: {selected_item}")
            ui.notify("选择的数据集格式无效", type='negative')
    
    def delete_selected_dataset(self):
        """删除选中的数据集"""
        selected = self.dataset_table.selected
        if not selected:
            ui.notify("请先选择一个数据集", type='warning')
            return
        
        dataset_name = selected[0]['name']
        try:
            self.dataset_manager.delete_dataset(dataset_name)
            self.refresh_datasets()
            self.preview_table.columns = []
            self.preview_table.rows = []
            self.preview_table.update()
            ui.notify(f"已删除数据集: {dataset_name}", type='positive')
        except Exception as ex:
            logger.error(f"删除数据集失败: {ex}")
            ui.notify(f"删除数据集失败: {str(ex)}", type='negative')
    
    async def send_message(self):
        """发送消息"""
        message = self.message_input.value.strip()
        if not message:
            ui.notify("消息不能为空", type='warning')
            return
        
        # ui.timer(0.01, lambda: asyncio.create_task(self.process_user_reply(message)), once=True)
        await self.process_user_reply(message)

        # 用户发言
        # self.user.say(message)
        
        # asyncio.sleep(0.01)
        # 清空输入框
        self.clear_input()
        
        # 异步处理回复
        # ui.timer(0.1, lambda: process_agent_reply(), once=True)
        # ui.timer(0.01, lambda: asyncio.create_task(self.process_agent_reply(message)), once=True)
        asyncio.create_task(self.process_agent_reply(message))

    async def process_user_reply(self,message):
        coordinator=self.chat_box.coordinator
        await self.user.say(message)
        await asyncio.sleep(0.01)

    # 修改process_agent_reply方法中的update_msg调用
    async def process_agent_reply1(self,message):
        coordinator=self.chat_box.coordinator
        # 显示"思考中"状态
        await coordinator.say([TextElement("请稍等，正在协调合适的助手解答你的问题...")])
        await asyncio.sleep(0.01)        

        # 获取协调agent的回复，这是一个生成器数组
        replyGenerator =await coordinator.process_message(message, self.chat_box.messages)
        preAnswer = ""
        agents=None
        for answer in replyGenerator:
            if answer.summary is not None:
                agents=answer
                newToken =answer.summary.replace(preAnswer,"")
                for c in newToken:#产生逐字输出的效果
                    preAnswer+=c
                    await asyncio.sleep(0.02)
                    await coordinator.update_msg(preAnswer,element_index=0,state="running") 
        
        # 判断agents里面的agent是否有重复，有则合并问题给到同一个agent
        agent_map={}
        for agent in agents.chatAgent:
            if agent.name in agent_map:
                agent_map[agent.name].question+=","+agent.question #组合问题给同一个agent
            else :
                agent_map[agent.name]=agent
        agent_arr = list(agent_map.values())
        # agents.chatAgent=agent_arr
        if len(agent_arr)>0:
            for agentInfo in agent_arr:
                # await self.coordinator.update_msg(agent.name,element_index=0)
                agent=coordinator.agents[agentInfo.name]
                await agent.say("好的，我来处理以下问题:"+agentInfo.question)
                await agent.say(SpinnerElement("思考中"))
                await asyncio.sleep(0.05)
                gen=agent.process_message(agentInfo.question,self.chat_box.messages)
                index=0
                async for result in gen:
                    if isinstance(result,list):#这部分要展示的OutputElement数组
                        for r in result:
                            index+=1
                            await asyncio.sleep(0.5)
                            if r.update_flag:
                                print("===rrrrrrr====")
                                await agent.update_msg(r,element_index=0,state="running")
                            else:
                                if index==1:
                                    print("===uuuuuuuuuuu====")
                                    await agent.update_msg(r,element_index=0,state="running")
                                else:
                                    print("===iiiiiiiiiiiii====")
                                    await agent.insert_msg(r)
                            # if first:
                            #     await agent.say(r)
                            # else:
                            #     await agent.insert_msg(r)
                    elif isinstance(result,str):#如果只是字符串，那么表示动态输出
                        
                        index+=1
                        await asyncio.sleep(0.5)
                        if index==1:
                            print("===eeeeeeeeeeee====")
                            await agent.update_msg(result,element_index=0,state="running")
                        else:
                            print("===yyyyyyyyyy====")
                            await agent.insert_msg(result)

    async def process_agent_reply(self, message):
        coordinator = self.chat_box.coordinator
        
        # try:
        # 显示初始状态（添加心跳机制）
        await coordinator.say([TextElement("请稍等，正在协调合适的助手解答你的问题...")])
        await asyncio.sleep(0.01)

        # 获取回复生成器
        # reply_generator = await coordinator.process_message(message, self.chat_box.messages)
        # 移除await（因为process_message现在返回异步生成器）
        reply_generator = coordinator.process_message(message, self.chat_box.messages)
        
        pre_answer = ""
        agents = None
        
        # 异步迭代处理回复
        async for answer in reply_generator:
            if answer.summary is not None:
                agents = answer
                new_token = answer.summary.replace(pre_answer, "")
                for c in new_token:
                    pre_answer += c
                    await coordinator.update_msg(pre_answer, element_index=0, state="running")
                    await asyncio.sleep(0.05)  # 让出事件循环控制权

    
        # 后续处理逻辑（保持原有逻辑，增加异常处理）
        if agents and len(agents.chatAgent) > 0:
            agent_map = {}
            for agent in agents.chatAgent:
                if agent.name in agent_map:
                    agent_map[agent.name].question += "," + agent.question
                else:
                    agent_map[agent.name] = agent
            
            agent_arr = list(agent_map.values())
            
            # 并行处理多个agent回复
            tasks = []
            for agent_info in agent_arr:
                tasks.append(
                    self.process_single_agent_reply(agent_info)
                )
            await asyncio.gather(*tasks)
                
        # except asyncio.CancelledError:
        #     logger.info("任务被取消")
        # except Exception as e:
        #     logger.error(f"处理回复时发生异常: {e}")
        #     await coordinator.update_msg(f"处理过程中发生错误: {str(e)}", element_index=0, state="error")

    
    def clear_input(self):
        """清空输入框"""
        self.message_input.value = ''
    
    # 修改handle_keydown方法
    async def handle_keydown(self, e: events.KeyEventArguments):
        """处理键盘事件"""
        if hasattr(e, 'key') and e.key == 'Enter' and not e.shift:
            await self.send_message()
            if hasattr(e, 'args'):
                e.args['preventDefault']()


    # 分离单个agent处理逻辑
    async def process_single_agent_reply(self, agent_info):
        coordinator = self.chat_box.coordinator
        agent = coordinator.agents[agent_info.name]
        
        # try:
        await agent.say("好的，我来处理以下问题:" + agent_info.question)
        await agent.say(SpinnerElement("思考中"))
        await asyncio.sleep(0)

        # 异步获取生成器
        gen = agent.process_message(agent_info.question, self.chat_box.messages)
        index = 0
        
        # 异步迭代处理结果
        async for result in gen:
            if isinstance(result, list):
                for r in result:
                    index += 1                    
                    if r.update_flag:
                        await agent.update_msg(r, element_index=0, state="running")
                    else:
                        if index == 1:
                            await agent.update_msg(r, element_index=0, state="running")
                        else:
                            await agent.insert_msg(r)
            elif isinstance(result, str):
                index += 1
                await asyncio.sleep(0.5)
                if index == 1:
                    await agent.update_msg(result, element_index=0, state="running")
                else:
                    await agent.insert_msg(result)
                        
        # except Exception as e:
        #     logger.error(f"处理{agent_info.name}回复时出错: {e}")
        #     await agent.update_msg(f"处理过程中发生错误: {str(e)}", element_index=0, state="error")

@app.post("/sync_data/create_agent")
async def create_agent_api(request: Request):
    body = await request.json()
    print(f"create_agent request body:{body}")

    try:
        agent_infos = get_agent_infos(body["agentIdList"])

        # 更新助手
        # agents_dict = {}
        for agent_info in agent_infos:
            print(agent_info)
            agent = DataAnalysisAgent(name=agent_info["name"],role=agent_info["role"],llm=agent_info["llm"],correct_llm=agent_info["correct_llm"],datasets=agent_info["datasets"],avatar="https://cdn.quasar.dev/img/avatar4.jpg")
            gen=agent.process_message("统计有多少个用户", chat_context=[])
            result=""
            async for r in gen:
                result=r
                print(result)
            
        #     agent.current_chatbox = app.chat_box
        #     agents_dict[agent_info["name"]] = agent
        #   app.chat_box.coordinator.agents = agents_dict

        # 创建聊天室
        #   agents = []
        #   for agent_info in agent_infos:
        #     print(agent_info)
        #     agents.append(DataAnalysisAgent(name=agent_info["name"],role=agent_info["role"],llm=agent_info["llm"],correct_llm=agent_info["correct_llm"],datasets=agent_info["datasets"],avatar="https://cdn.quasar.dev/img/avatar4.jpg"))
        #   coordinator_agent = CoordinatorAgent(agents=agents,llm=dsv3,avatar="https://cdn.quasar.dev/img/avatar3.jpg")
        #   app.chat_box = ChatBox(app.user,coordinator_agent)

        return HttpResponse.success()
    except Exception as e:
        logger.exception(f"create_agent Exception: {e}")
        err_msg = str(e)
    return HttpResponse.error(500, err_msg)


# ====================== 启动应用 ======================
 
if __name__ in {"__main__", "__mp_main__"}:
    app = MultiAgentChatApp()
    print('++++++++++++++++')
    ui.run(title="多智能体协作聊天系统", port=8081, reload=True) 