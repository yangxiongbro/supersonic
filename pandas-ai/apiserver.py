from fastapi.middleware.cors import CORSMiddleware
from nicegui import ui, app
from chatbox.agents.agents import *
from extensions.llms.openai.pandasai_openai import OpenAI
from fastapi.responses import JSONResponse
from fastapi import Request
from sync_data.sync_data_common import ss_db_info
from sync_data.sync_schema import create_schema, delete_schema, update_schema
from sync_data.sync_agent import get_agent, delete_agent
from common.http_response import HttpResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
OpenAI._supported_chat_models.append("deepseek-ai/DeepSeek-V3")
dsv3 = OpenAI(max_tokens=8192,temperature=0,model="deepseek-v3-241226",api_token="8e8723a1-8032-4213-9752-748fbd9fbd70",api_base="https://ark.cn-beijing.volces.com/api/v1")

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
    该Agent是一位一线和二线投诉工单基础信息分析专家，它掌握数据集包含：
    1、一线投诉工单基础信息：该数据集包含工单创建时间、省份、业务、服务请求分类1、服务请求分类2、服务请求分类3、服务请求分类4、服务请求分类5、一线客服流水、二线工单号、二线工单内容、省份或二线、全球通身份等级、用户星级、在统一客服系统停留时长、在集中客服团队停留时长、是否满意、紧急程度、用户姓名、手机号码、工单归档时间、24小时口径处理时长、互联网侧时长、首回复时长、是否24小时超时、是否分层分级超时、是否首回复16小时超时等信息。其中维度为工单创建时间、省份、业务、服务请求分类1、服务请求分类2、服务请求分类3、服务请求分类4、服务请求分类5、一线客服流水、二线工单号、省份或二线、全球通身份等级、用户星级、工单归档时间，指标为二线工单内容、24小时口径处理时长、互联网侧时长、首回复时长、是否24小时超时、是否分层分级超时、是否首回复16小时超时
    2、二线投诉工单基础信息：该数据集包含了一线投诉工单的明细数据，可以查询一线投诉工单的数量，创建时间，工单内容，处理内容等
    基于以上数据，可以通过多维度分析二线投诉工单数据，并将分析结果生成表格和绘制图表，它擅长绘制柱状图、饼图、折线图、玫瑰图、面积图、散点图、环形图
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

# 创建schema
@app.post("/sync_data/create_schema")
async def create_schema_api(request: Request):
    body = await request.json()
    logger.info(f"create_schema request body:{body}")

    try:
        datasets = create_schema(body["schemaInfos"])

#   agent = app.chat_box.coordinator.agents["互联网用户分析助手"]
#   for dataset in datasets:
#     agent.datasets.append(dataset)

    # for key in agents:
    #   agent = agents[key]
    #   if isinstance(agent, DataAnalysisAgent):
    #     app.chat_box.coordinator.agents[key].datasets.append(path)

        return HttpResponse.success(len(datasets))
    except Exception as e:
        logger.exception(f"create_schema Exception: {e}")
        err_msg = str(e)
    return HttpResponse.error(500, err_msg)

# 删除schema
@app.post("/sync_data/delete_schema")
async def delete_schema_api(request: Request):
    body = await request.json()
    print(f"delete_schema request body:{body}")

    try:
        datasets = delete_schema(ss_db_info, body["modelIdList"])
        return HttpResponse.success(len(datasets))
    except Exception as e:
        logger.exception(f"delete_schema Exception: {e}")
        err_msg = str(e)
    return HttpResponse.error(500, err_msg)

# 更新schema
@app.post("/sync_data/update_schema")
async def update_schema_api(request: Request):
    body = await request.json()
    print(f"update_schema request body:{body}")

    try:
        datasets = update_schema(body["schemaInfos"])
        return HttpResponse.success(len(datasets))
    except Exception as e:
        logger.exception(f"update_schema Exception: {e}")
        err_msg = str(e)
    return HttpResponse.error(500, err_msg)

# 删除助手
@app.post('/sync_data/delete_agent')
async def update_agent_api(request: Request):
    body = await request.json()
    print(f"delete_agent request body:{body}")

    try:
        delete_agent_ids = delete_agent(body["agentIdList"])
        return HttpResponse.success(len(delete_agent_ids))
    except Exception as e:
        logger.exception(f"delete_agent Exception: {e}")
        err_msg = str(e)
    return HttpResponse.error(500, err_msg)

# 问答助手
@app.post('/agent/execute')
async def chatdata(request: Request):
    body = await request.json()
    logger.info(f"agent execute request body:{body}")
    '''
    1、通过助手ID去获取助手的基本信息，名称、
    2、获取助手大模型配置，实例化大模型，有生成sql模型和纠正模型
    3、读取助手的数据集
    4、实例化一个agent
    '''
    err_msg=""
    try:
        agent=get_agent(body["agentId"], body.get("chatId", None))
        gen=agent.process_message(body["queryText"], chat_context=[])
        result=[]
        async for r in gen:
            result=r
        logger.exception(f"result：{result}")
        if len(result) >0:
            # 判断有没有错误
            if "err_info" in result[0]:
                return HttpResponse.error(500, result[0]["err_info"])
        for r in result:
            data = r.get("data", None)
            if  isinstance(data, pd.DataFrame):
                r["data"]=data.to_dict(orient='records')
        return HttpResponse.success(result)
    except Exception as e:
        logger.exception(f"创建失败: {e}")
        err_msg = str(e)
    return HttpResponse.error(500, err_msg)

@app.get('/getAgents')
async def getAgents():
    result={}
    for el in agent_arr:
        result[el.name]=el.role
    return JSONResponse(content=result)

# 运行应用
ui.run(port=8081, reload=False)