import requests
import json

API_HOST = "http://192.168.16.22:8080"
API_KEY = "ragflow-MwMDI2MWJhMWVjOTExZjBiNDFkMDI0Mm"
AGENT_ID = "bbd62fa61ec811f08aa40242ac190006"
question = "spring 使用什么版本"

# 请求url
url = API_HOST + "/api/v1/agents/" + AGENT_ID + "/completions"
# print(url)

# 自定义请求头
headers = {
    "Authorization": "Bearer %s" % API_KEY,
    "Content-Type": "application/json",
}


class AgentStreamResponse:
    def __init__(self, arg1):
        self.arg1 = arg1

    def get_session_id(self):
        """
        获取会话 ID
        """
        data = {"id": AGENT_ID}
        response = requests.post(url, data=data, headers=headers)
        try:
            line_list = []
            with requests.post(
                url, json=data, headers=headers, stream=True, timeout=30
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

    def get_stream_data(self):
        """
        获取流式数据（生成器版本）
        每次从流中读取一行有效数据并返回
        """
        try:
            session_id = self.get_session_id()
            data = {
                "id": AGENT_ID,
                "question": self.arg1,
                "stream": "true",
                "session_id": session_id,
            }
            with requests.post(
                url, json=data, headers=headers, stream=True, timeout=30
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:  # 过滤掉空行
                            decoded_line = line.decode("utf-8")
                            print(f"原始数据: {decoded_line}")  # 调试信息

                            # 检查是否是有效的 JSON 数据行
                            if decoded_line.startswith("data:"):
                                try:
                                    # 提取 JSON 数据部分
                                    line_row = decoded_line.split("data:")[1]
                                    line_dict = json.loads(line_row)

                                    # 提取 answer 字段（如果存在）
                                    if "data" in line_dict and not isinstance(line_dict["data"],bool) and "answer" in line_dict["data"] :
                                        answer = line_dict["data"]["answer"]
                                        yield answer  # 返回解析后的 answer
                                except json.JSONDecodeError as e:
                                    print(f"JSON 解析错误: {e}")
                                    continue
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None

agent_stream_response = AgentStreamResponse(question)
result = agent_stream_response.get_stream_data()
for r in result:
    print(r)

# def main(arg1: str) -> dict:
#     agent_stream_response = AgentStreamResponse(arg1)
#     result = agent_stream_response.get_stream_data()
#     return {
#         "result": result,
#     }