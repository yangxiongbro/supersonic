
from typing import List, Union, Optional, Dict, Any
import pandas as pd
from .output.output_element import *
from .datamanager.dataset_mamaner import DatasetManager
from .datamanager.dbmanager import DatabaseManager
from .agents.agents import *
from .output.visrender.vis_render import (
    table_vis_render,
    render_chart_default,
    chart_vis_render
)
from datetime import datetime
from nicegui import ui
AGENT_CHAT_COLOR='grey-2'
USER_CHAT_COLOR='grey-2'


class ChatBox:
    """聊天室模型"""
    def __init__(self, user: User,coordinator:CoordinatorAgent):
        self.user = user
        self.user.current_chatbox = self
        # self.agents = agents
        self.coordinator=coordinator
        self.coordinator.current_chatbox=self
        
        for key in coordinator.agents:
            coordinator.agents[key].current_chatbox = self
        self.messages = []
        self.ui_messages = []
        self.chat_container = None
        self.message_id_counter = 0
    
    async def add_user_message(self, elements: List[OutputElement]):
        """添加用户消息"""
        message_id = f"msg_{self.message_id_counter}"
        self.message_id_counter += 1
        
        message = {
            'id': message_id,
            'sender': self.user,
            'elements': elements,
            'timestamp': datetime.now(),
            'is_user': True
        }
        self.messages.append(message)
        
        if self.chat_container:
            with self.chat_container:
                await self._render_message(message)
    
    async def add_agent_message(self, agent: ChatAgent, elements: List[OutputElement]):
        """添加智能体消息"""
        message_id = f"msg_{self.message_id_counter}"
        self.message_id_counter += 1
        
        message = {
            'id': message_id,
            'sender': agent,
            'elements': elements,
            'timestamp': datetime.now(),
            'is_user': False
        }
        self.messages.append(message)
        
        if self.chat_container:
            with self.chat_container:
                await self._render_message(message)
    
    async def update_agent_message(self, agent: ChatAgent, element: OutputElement, element_index: int, state: str):
        """更新智能体消息"""
        # 查找最后一条来自该智能体的消息
        for msg in reversed(self.messages):
            if msg['sender'] == agent and not msg['is_user']:
                if element_index < 0 or element_index >= len(msg['elements']):
                    msg['elements'].append(element)
                else:
                    msg['elements'][element_index] = element
                
                msg['state'] = state
                msg['timestamp'] = datetime.now()
                
                # 更新UI
                if self.chat_container:
                    await self._update_ui_message(msg)
                break
    
    async def insert_agent_message(self, agent: ChatAgent, element: OutputElement):
        """插入智能体消息"""
        # 查找最后一条来自该智能体的消息
        for msg in reversed(self.messages):
            if msg['sender'] == agent and not msg['is_user']:
                msg['elements'].append(element)
                msg['timestamp'] = datetime.now()
                
                # 更新UI
                if self.chat_container:
                    await self._update_ui_message(msg)
                break
    
    async def _render_message(self, message: Dict):
        """渲染单条消息到UI"""
        # with ui.card().classes('w-full p-4 my-2') as card:
        stamp=message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        # avatar=message['sender'].avatar
        is_sender=message['is_user']
        avatar=message['sender'].avatar
        name=message['sender'].name
        for element in message['elements']:
            
            with ui.chat_message(name=name,avatar=avatar,stamp=stamp,sent=is_sender) as card:

                # card.style('width:50%')
                # card.classes('bg-blue-100' if message['is_user'] else 'bg-gray-100')
                card.classes('ml-auto' if message['is_user'] else 'mr-auto')
                # card.classes("overflow-x-auto p-2 rounded-lg bg-gray-100")
                # card.style("max-width:80%")
                card.classes("max-w-full")
                card.props("size=11")

                card.props(f'bg-color={USER_CHAT_COLOR}') if message['is_user'] else card.props(f'bg-color={AGENT_CHAT_COLOR}')
                
                # with ui.row().classes('items-center'):
                #     ui.image(message['sender'].avatar).classes('w-8 h-8 rounded-full')
                #     ui.label(message['sender'].name).classes('font-bold ml-2')
                
                await self._render_element(element)
            
            # ui.label(message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')).classes('text-xs text-gray-500 mt-2')
        
        self.ui_messages.append({'id': message['id'], 'card': card})
    
    async def _update_ui_message(self, message: Dict):
        """更新UI中的消息"""
        for ui_msg in self.ui_messages:
            if ui_msg['id'] == message['id']:
                # 清除旧内容
                for child in list(ui_msg['card']):
                    child.delete()
                
                # 重新渲染
                stamp=message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                # avatar=message['sender'].avatar
                is_sender=message['is_user']
                avatar=message['sender'].avatar
                with ui_msg['card'] as card:
                    # with ui.row().classes('items-center'):
                    #     ui.image(message['sender'].avatar).classes('w-8 h-8 rounded-full')
                    #     ui.label(message['sender'].name).classes('font-bold ml-2')
                    card.props(f'bg-color={AGENT_CHAT_COLOR}')
                    for element in message['elements']:
                        await self._render_element(element)
                    
                    # ui.label(message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')).classes('text-xs text-gray-500 mt-2')
                break
    

        
    async def _render_element(self, element: OutputElement):
        element.render()
        await asyncio.sleep(0)

        # """渲染输出元素"""
        # if isinstance(element, TextElement):
        #     ui.label(element.content).classes('whitespace-pre-wrap')
        # elif isinstance(element, SpinnerElement):
        #     with ui.row():
        #         if element.text is not None:
        #             ui.label(element.content).classes('whitespace-pre-wrap')
        #         # ui.spinner(size='30px')
        #         ui.spinner(type=element.type,size=element.size,color=element.color)
        # elif isinstance(element, MarkdownElement):
        #     ui.markdown(element.content)
        # elif isinstance(element, ImageElement):
        #     ui.image(element.content).classes('max-w-full')
        # elif isinstance(element, DataFrameElement):
        #     df = pd.DataFrame(element.content)
        #     # 转换 DataFrame 为字典，并处理 Timestamp 类型
        #     # columns_info=element.columns_info
        #     # if columns_info is None:
        #     # 转换所有 Timestamp 列为字符串
        #     for col in df.columns:
        #         if pd.api.types.is_datetime64_any_dtype(df[col]):
        #             df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
        #         columns_info=[{'name': col, 'label': col, 'field': col,"sortable": True} for col in df.columns]
                    
        #     # 创建表格
        #     table_data=df.to_dict('records')
        #     table=ui.table(
        #         columns=columns_info,         
        #         rows=table_data
        #     ).classes('w-full max-h-64 overflow-auto')
        #     if element.table_vis_config is not None:                
        #         table_vis_render(table,table_data,element.table_vis_config)
        #     # if element.slot_info is not None:
        #     #     #添加add_slot
        #     #     for key in element.slot_info:
        #     #         print(element.slot_info[key])
        #     #         table.add_slot(key,element.slot_info[key])
        #     #         # table.add_slot('body-cell-缺陷总数', '''<q-td key="缺陷总数" :props="props"><q-badge :color="props.value > 10 ? 'red' : 'green'">{{props.value}}</q-badge></q-td>''')
                
        # elif isinstance(element, EChartElement):
        #     # 修正图的默认样式
        #     options=render_chart_default(element.content,element.data) 
        #     #设置一些用户要求的样式
        #     # if element.vis_config is not None:                
        #     #     chart_vis_render(options,element.vis_config)    
        #     # theme=json.loads("/home/fs-user/project/pandasai/pandas-ai/chatbox/visrender/sheme/walden.project.json")
        #     if options is not None:
        #         echart=ui.echart(options).classes('w-full h-64')
        #     # ecahrt.run_chart_method("registerTheme")
        # elif isinstance(element, HighChartElement):
        #     ui.highchart(element.content).classes('w-full h-64')
        # else:
        #     ui.label(str(element.content)).classes('whitespace-pre-wrap')
        
        # self.chat_container.scroll_to(percent=100) 