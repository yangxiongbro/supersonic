import requests
import json
import logging
import asyncio
from typing import List, Dict, Any
from .agents import ChatAgent
from chatbox.output.output_element import MarkdownElement

class RagflowAgent(ChatAgent):
    """协调智能体"""
    def __init__(self,name:str=None,role:str=None,api_host:str=None,api_key:str=None,agent_id:str=None,*args, **kwargs):
        if name is None:
            name="知识库" 
        if role is None:
            role="rag知识库助手"
        super().__init__(name=name, llm=None,role=role,*args, **kwargs)
        self.api_host = api_host
        self.api_key = api_key
        self.agent_id = agent_id


        # 请求url
        self.url = self.api_host + "/api/v1/agents/" + self.agent_id + "/completions"

# 自定义请求头
        self.headers = {
            "Authorization": "Bearer %s" % self.api_key,
            "Content-Type": "application/json",
        }

    async def _get_session_id(self):
        """
        获取会话 ID
        """
        data = {"id": self.agent_id}
        response = requests.post(self.url, data=data, headers=self.headers)
        try:
            line_list = []
            with requests.post(
                self.url, json=data, headers=self.headers, stream=True, timeout=30
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:  # 过滤掉空行
                            # print(line.decode("utf-8"))
                            line_list.append(line.decode("utf-8"))
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    return False

            # print("line_list",line_list)

            first_line = line_list[0]
            # 提取data内容
            line_row = first_line.split("data:")[1]
            # json解析
            line_dict = json.loads(line_row)
            # 获取session_id
            session_id = line_dict["data"]["session_id"]
            return session_id
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return False

    async def _get_stream_data(self,message):
        """
        获取流式数据（生成器版本）
        每次从流中读取一行有效数据并返回
        """
        try:
            session_id = await self._get_session_id()
            data = {
                "id": self.agent_id,
                "question": message,
                "stream": "true",
                "session_id": session_id,
            }
            with requests.post(
                self.url, json=data, headers=self.headers, stream=True, timeout=30
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:  # 过滤掉空行
                            yield line
                else:
                    yield f"请求错误"
                    # print(f"请求失败，状态码: {response.status_code}")
                    # return None
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            yield f"请求错误"

    
    async def process_message(self, message: str, chat_context: List[Dict]):
        result = self._get_stream_data(message)
        async for line in result:
            if not isinstance(line, bytes):
                continue
            decoded_line = line.decode("utf-8")
            # 检查是否是有效的 JSON 数据行
            if decoded_line.startswith("data:"):
                try:
                    # 提取 JSON 数据部分
                    line_row = decoded_line.split("data:")[1]
                    line_dict = json.loads(line_row)

                    # 提取 answer 字段（如果存在）
                    if "data" in line_dict and not isinstance(line_dict["data"],bool) and "answer" in line_dict["data"] :
                        answer = line_dict["data"]["answer"]                                        
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {e}")
                    continue
            me=MarkdownElement(answer)
            me.update_flag=True
            yield [me]
            await asyncio.sleep(0)
    
    async def async_generator_wrapper(self,sync_gen): 
        """将同步生成器包装为异步生成器"""
        for item in sync_gen:
            yield item
            await asyncio.sleep(0)  # 让出事件循环控制权    





