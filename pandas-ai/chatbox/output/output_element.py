from abc import ABC, abstractmethod
from nicegui import ui
import pandas as pd
from dataclasses import dataclass
from typing import List, Union, Optional, Dict, Any
from enum import Enum, auto
from nicegui.elements.spinner import SpinnerTypes
from .visrender.vis_render import (
    table_vis_render,
    render_chart_default,
    chart_vis_render
)
class OutputType(Enum):
    """输出元素类型枚举"""
    TEXT = auto()
    SPINNER = auto()
    MARKDOWN = auto()
    IMAGE = auto()
    DATAFRAME = auto()
    ECHART = auto()
    HIGHCHART = auto()
    SQL = auto()
    CUSTOM = auto()

@dataclass
class OutputElement(ABC):
    """输出元素基类"""
    
    content: Any
    output_type: OutputType
    update_flag:bool=False
    def to_dict(self) -> Dict:
        """将输出元素转换为字典"""
        return {
            'type': self.output_type.name,
            'content': self.content,
            'style': self.style or {}
        }
    @abstractmethod
    def render(self):
        pass

class TextElement(OutputElement):
    """文本输出元素"""
    def __init__(self, text: str, *args, **kwargs):
        super().__init__(content=text, output_type=OutputType.TEXT, *args, **kwargs)
    
    def render(self):
        ui.label(self.content).classes('whitespace-pre-wrap')

class SpinnerElement(OutputElement):
    """等待元素"""
    def __init__(self, text:Optional[str]=None, type:Optional[SpinnerTypes]='default',size:Optional[str]='30px',color:Optional[str]='green',*args, **kwargs):
        self.text=text
        self.type=type
        self.size=size
        self.color=color
        super().__init__(content=text, output_type=OutputType.SPINNER,*args, **kwargs)

    def render(self):
        with ui.row():
            if self.text is not None:
                ui.label(self.content).classes('whitespace-pre-wrap')
            # ui.spinner(size='30px')
            ui.spinner(type=self.type,size=self.size,color=self.color)     

class MarkdownElement(OutputElement):
    """Markdown输出元素"""
    def __init__(self, markdown: str, *args, **kwargs):
        super().__init__(content=markdown, output_type=OutputType.MARKDOWN,*args, **kwargs)

    def render(self):
        ui.markdown(self.content) 

class SQLElement(OutputElement):
    """Markdown输出元素"""
    def __init__(self, sql:str,explain: str, *args, **kwargs):
        self.explain=explain
        super().__init__(content=sql, output_type=OutputType.SQL,*args, **kwargs)   

    def render(self):
        with ui.expansion('SQL', icon='work').classes('w-full'):
            ui.markdown(f"{self.explain}") 
            ui.markdown(f"```sql\n{self.content}\n```")      


class ImageElement(OutputElement):
    """图片输出元素"""
    def __init__(self, image_path_or_url: str, *args, **kwargs):
        super().__init__(content=image_path_or_url, output_type=OutputType.IMAGE, *args, **kwargs)

    def render(self):
        ui.markdown(self.content) 

# class DataFrameElement(OutputElement):
#     """数据框输出元素"""
#     def __init__(self, dataframe: pd.DataFrame, style: Optional[Dict] = None):
#         super().__init__(content=dataframe.to_dict('records'), output_type=OutputType.DATAFRAME, style=style)
class DataFrameElement(OutputElement):
    """数据框输出元素"""
    def __init__(self, title:str,explanatory:str,dataframe: pd.DataFrame, columns_info:Optional[List]=None,table_vis_config:dict=None,*args, **kwargs):
        self.title=title
        self.explanatory=explanatory
        self.columns_info=columns_info #扩展一个列属性
        self.table_vis_config=table_vis_config
        # 转换所有 Timestamp 列为字符串
        df = dataframe.copy()
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
        
        super().__init__(content=df.to_dict('records'), output_type=OutputType.DATAFRAME, *args, **kwargs)

    def render(self):
        df = pd.DataFrame(self.content)
        # 转换 DataFrame 为字典，并处理 Timestamp 类型
        # columns_info=element.columns_info
        # if columns_info is None:
        # 转换所有 Timestamp 列为字符串
        with ui.expansion(self.title, icon='work',value=True).classes('w-full'):
            # ui.markdown(self.explanatory)
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
                columns_info=[{'name': col, 'label': col, 'field': col,"sortable": True} for col in df.columns]
                    
            # 创建表格
            table_data=df.to_dict('records')
            table=ui.table(
                columns=columns_info,         
                rows=table_data
            ).classes('w-full max-h-64 overflow-auto')
            if self.table_vis_config is not None:                
                table_vis_render(table,table_data,self.table_vis_config)

class EChartElement(OutputElement):
    data:pd.DataFrame
    """EChart图表输出元素"""
    def __init__(self,title:str, options: Dict, data:pd.DataFrame,vis_config:Optional[Dict] = None,*args, **kwargs):
        self.title=title
        self.data=data
        self.vis_config=vis_config
        super().__init__(content=options, output_type=OutputType.ECHART, *args, **kwargs)

    def render(self):
        # 修正图的默认样式
        options=render_chart_default(self.content,self.data) 
        #设置一些用户要求的样式
        # if element.vis_config is not None:                
        #     chart_vis_render(options,element.vis_config)    
        # theme=json.loads("/home/fs-user/project/pandasai/pandas-ai/chatbox/visrender/sheme/walden.project.json")
        if options is not None:
            with ui.expansion(self.title, icon='work',value=True).classes('w-full'):
                ui.echart(options).classes('w-full h-64')

class HighChartElement(OutputElement):
    """HighChart图表输出元素"""
    def __init__(self, options: Dict, *args, **kwargs):
        super().__init__(content=options, output_type=OutputType.HIGHCHART, *args, **kwargs)

    def render(self):
        pass