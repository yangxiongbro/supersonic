from mcp.server.fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware
from nicegui import ui, app
from chatbox.agents.agents import *
from extensions.llms.openai.pandasai_openai import OpenAI
from fastapi.responses import JSONResponse
import pandas as pd
mcp = FastMCP("chatdata")
OpenAI._supported_chat_models.append("deepseek-v3-250324")
OpenAI._supported_chat_models.append("deepseek-ai/DeepSeek-V3")
# dsv3 = OpenAI(max_tokens=8192,temperature=0,model="deepseek-v3-241226",api_token="8e8723a1-8032-4213-9752-748fbd9fbd70",api_base="https://ark.cn-beijing.volces.com/api/v1")
dsv3 = OpenAI(max_tokens=8192,temperature=0,model="deepseek-ai/DeepSeek-V3",api_token="sk-dkihzhdvaowvyastvjtnhutiyyfrsntqnptbpehuvbhfytzz",api_base="https://api.siliconflow.cn/v1")

agent_arr=[
    DataAnalysisAgentMarkdown(
            name="缺陷分析助手",
            role="""
        该Agent是一位项目缺陷数据分析专家，擅长通过研发项目所记录的缺陷清单分析项目的质量情况，它可以将数据生成表格和绘制图表，
        它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
        """,
        llm=dsv3,correct_llm=dsv3,datasets=['myorg/abug'],avatar="https://cdn.quasar.dev/img/avatar4.jpg")
        ,
    DataAnalysisAgentMarkdown(
            name="自行车销售分析助手",
            role="""
            该Agent是一位自行车销售数据分析专家，它掌握以下数据：
            1、自行车产品信息，可随时提供产品的详细信息
            2、客户信息，可提供客户的详细信息
            3、订单和订单详情
            4、门店信息，可提供售卖自行车产品的门店详细信息
            5、职员信息，可提供各门店职员的详细信息
            基于以上数据，可以将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
            """,
            llm=dsv3,correct_llm=dsv3,datasets=
                                        ['myorg/trino-mysql-brands','myorg/trino-mysql-categories',
                                         'myorg/trino-mysql-order','myorg/trino-mysql-order-items',
                                         'myorg/trino-mysql-store','myorg/trnio-mysql-products','myorg/trino-mysql-staffs',
                                         ],avatar="https://cdn.quasar.dev/img/avatar4.jpg")
            ,
    DataAnalysisAgentMarkdown(
            name="投诉工单基础信息分析助手",
            role="""
    该Agent是一位一线和二线投诉工单基础信息分析专家，它掌握2个数据集：
    1、一线投诉工单基础信息：该数据集包含工单创建时间、省份、业务、服务请求分类1、服务请求分类2、服务请求分类3、服务请求分类4、服务请求分类5、一线客服流水、二线工单号、二线工单内容、省份或二线、全球通身份等级、用户星级、在统一客服系统停留时长、在集中客服团队停留时长、是否满意、紧急程度、用户姓名、手机号码、工单归档时间、24小时口径处理时长、互联网侧时长、首回复时长、是否24小时超时、是否分层分级超时、是否首回复16小时超时等信息。其中维度为工单创建时间、省份、业务、服务请求分类1、服务请求分类2、服务请求分类3、服务请求分类4、服务请求分类5、一线客服流水、二线工单号、省份或二线、全球通身份等级、用户星级、工单归档时间，指标为二线工单内容、24小时口径处理时长、互联网侧时长、首回复时长、是否24小时超时、是否分层分级超时、是否首回复16小时超时
    2、二线投诉工单基础信息：该数据集包含了一线投诉工单的明细数据，可以查询一线投诉工单的数量，创建时间，工单内容，处理内容等
    这两个数据集是完全独立的，它们之间没有任何关联，也不会将两个数据集关联起来分析，基于以上数据，可以通过多维度分析投诉工单数据，并将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
    """,
    llm=dsv3,correct_llm=dsv3,
    datasets=['myorg/trino-dy-n1-tp-0005-base-count-byd','myorg/trino-dy-second-workorder-detail'],
    avatar="https://cdn.quasar.dev/img/avatar4.jpg")
    ,
    DataAnalysisAgentMarkdown(
            name="互联网产品满意度分析助手",
            role="""
    该Agent善于分析中国移动互联网的业务产品(简称互联网产品)在各季度的用户体验满意度评分数据，它可以：
    1、获取中国移动集团(简称集团)调研满意度调研的产品
    2、分析互联网产品在各季度的满意度得分情况
    基于以上数据，可以将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
    """,
    llm=dsv3,correct_llm=dsv3,datasets=
                                ['myorg/trino-dy-jiuan-manyidu-byq',
                                    ],avatar="https://cdn.quasar.dev/img/avatar4.jpg")             
]
agent_map={el.name:el for el in agent_arr}
@mcp.tool()
async def chatdata(name:str,question:str):
    """
    根据用户的问题调用数据助手从数据库获得数据，同时可以绘制图表

    Args:
    name: 助手名称，必须提供
    question:用户的问题，必须提供
    Returns:
        返回结果
    """    
    agent=agent_map[name]
    gen=agent.process_message(question,chat_context=[])
    result=""
    async for r in gen:
        result=r
    result_str=""
    for r in result:
        if  isinstance(r["data"], pd.DataFrame):
            r["data"]=r["data"].to_dict(orient='records')


    for el in result:
        title = el.get("title", "")
        if title:
            result_str+= f"{title}  \n"

        explanatory = el.get("explanatory", "")
        if explanatory:
            result_str+= f"{explanatory}  \n"

        data = el.get("data")
        if data:
            df = pd.DataFrame(data)
            data_markdown = df.to_markdown()
            result_str+= f"{data_markdown}  \n"

        sql = el.get("sql")
        if sql:
            result_str+= f'\n  \n生成的sql语句  \n```sql\n{sql}\n```'

        sql_explain = el.get("sql_explain")
        if sql_explain:
            result_str+= f'  \n{sql_explain}  \n'



    return result_str



if __name__ == "__main__":
    asyncio.run(mcp.run(transport="streamable-http"))