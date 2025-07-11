class PythonCode {
  code string @description(#"
    Used to store the generated Python code
  "#)
}

function GenPythonCode(prompt:string) -> PythonCode {
  client DeepSeekV3
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    {{prompt}}

    {{ ctx.output_format }}
  "#
}

test TestGenPythonCode {
  functions [GenPythonCode]
  args {
    prompt #"
      You already have access to the following dataset: 
    <tables>
    
    <table dialect="duckdb" table_name="abug" description="abug" dimensions="342x7">
    <sample_data>
    行号,缺陷状态,开发人员,概要,提出日期,关闭时间,异常原因
    1,处理中,wangxiaofang,【bug】标注管理台->标注模板管理-定制化模板：【另存为】模板时，调错接口，并且用户信息为空,2025/3/3 16:31,,Code Error
    2,已关闭,zhoujunwei,【bug】多模态语料库->纯数据集管理：数据集本来是公开状态，在编辑页面修改公开范围后进行审核通过，公开范围没有成功改变,2025/2/8 18:36,2025/2/12 11:15,Code Error
    3,开放,linpeiliang, 【bug】标注管理台->智能标注模型管理：能力名称、类型需要与能力清单一致,2025/1/21 10:16,,Requirements
    4,开放,zhoujunwei,【bug】多模态语料库->标注数据集管理：审核通过以后，纯数据集是能正常使用的，但是和纯数据关联的标注数据集无法显示,2025/2/8 18:28,,Code Error
    5,已关闭,zhoujunwei,【bug】公共管理模块->FTP信息管理：条件筛选无效果；查询关键字报错,2025/2/21 16:22,2025/2/27 18:53,Code Error
    </sample_data>
    <columns description="Refer to the following field definition information when generating SQL.">
    <column name="行号" type="integer"/>
    <column name="缺陷状态" type="string"/>
    <column name="开发人员" type="string"/>
    <column name="概要" type="string"/>
    <column name="提出日期" type="string"/>
    <column name="关闭时间" type="string"/>
    <column name="异常原因" type="string"/>
    </columns>
    </table>
    
    
    </tables>
    
    你可以使用以下工具:
    - execute_sql_query(sql_query: str) -> pd.Dataframe
        该工具连接数据，执行sql查询并返回pd.Dataframe
    
    Based on the dataset information and tools provided above, generate Python code for the USER QUERY.
    If the user's question is not clear enough, do not forcibly generate SQL. Feedback information should be provided to the user, asking them to provide more details.
    Before generating the code, refer to the #Note section for instructions on how to generate the code_unit_dict.
    
    
    
    ### USER QUERY
     统计数据
    
    #Note：Below are the requirements for generating Python code, which must be followed:
    - At the end, must declare "result" variable as a list to store each generated code unit dictionary, for example:
    
       result=[code_unit_dict_1, code_unit_dict_2, ...] #Very important: The variable name must be "result" and should not be preceded by a definition like "def", otherwise an error will occur.
       
    - Generate python code and return full updated code,code comments are written in Chinese.
    - Important: When encountering complex problems, it is essential to first break down the problem into steps that involve obtaining simpler datasets. Then, merge and compute each step's data to derive the final result.
    - Important: Do not create database connections and query methods on your own. You must use the execute_sql_query tool for SQL queries.
    - When writing SQL,it is essential to strictly adhere to the database dialect to generate the correct SQL syntax, particularly focusing on the SQL functions used.
    - When writing SQL,only relevant table for query and do aggregation, sorting, joins and grouby through sql query.
    - When writing SQL, if you encounter an ORDER BY clause, do not enclose the fields in single quotes. For example, ORDER BY '年龄' is incorrect.
    - When writing SQL, using two consecutive percent signs in the date formatting function is incorrect. For example, DATE_FORMAT(date_field, '%%Y-%%m') is wrong. The correct format should use single percent signs, such as '%Y-%m'.
    - When writing SQL, the field names used in the ORDER BY clause should be consistent with the aliases defined in the SELECT portion.
    - Since generating SQL statements frequently results in errors when involving date handling, it is essential to thoroughly study the content in the '#SQL Date Handling' section first.
    - Important: The code for fetching data and generating visualization objects must be organized as a complete code unit. The code of one unit must be organized together,if there are multiple code units.Refer to the following steps to generate a unit of code:
    -- Step1: Define a dictionary to hold code unit variables
      This dict is used to store together all variables that a code unit intends to display,it must be a global variable. The dict should be named uniquely across the global scope. The schema for the dict is as follows:
      code_unit_dict_1={
        "sql":"<SQL query to generate data>",
      "sql_explain":"<Detailed explanation of the logic behind SQL statement generation>",
      "question":"<Describe the user's question regarding this SQL query in a way that humans can understand>",
        "title":"<The title should reflect the business significance of the data>",
        "explanatory":"<the explanatory text should make it easy for humans to understand the business context of the data>",
        "data":<dataframe instance>,
      "nicegui_table_columns":<nicegui_table columns information>,
      "nicegui_table_add_slots_info":<A dictionary to store the parameters of add_slot, where the key is the value of the name parameter, and the value is the value of the template parameter>
        "chart":<echart config>
      }
    
    -- Step2: Obtain a DataFrame
        First, you need to obtain a DataFrame by executing an SQL query. Here’s an example of how to do this:
        code_unit_dict_1={}
        df_1 = execute_sql_query(sql_query)
        code_unit_dict_1["sql"]=sql_query
        code_unit_dict_1["sql_explain"]="从员工表进行统计，通过count(员工ID)函数获取员工总数"
        code_unit_dict_1["data"]=df_1
        code_unit_dict_1["question"]="统计员工总人数"
    
    -- Step3: DataFrame会用表格进行展示，分析用户问题是否额外要求生成表格的可视化配置
        必须通过学习'# 表格可视化配置'章节内容正确设置config_item_name和config值：
        table_visualization_config1={
          config_item_name1:config1,
          config_item_name2:config2,
          ...
          ...
        }
        code_unit_dict_1["table_visualization_config"]=table_visualization_config1
    
    -- Step4: Display titles and explanatory text  
        The title should reflect the business significance of the data, and the explanatory text should make it easy for humans to understand the business context of the data.For example:
        title_var_1='每个职员的订单数量统计'
        explanatory_var_1='以下表格展示了每位员工在不同门店处理的订单数量。'
        code_unit_dict_1["title"]=title_var_1
        code_unit_dict_1["explanatory"]=explanatory_var_1
    
    -- Step5: 请判断用户是否有示绘制图表意图,如果有则按照以下规范生成图表的可视化配置,在生成可视化配置前必须先学习'#图表可视化配置'章节内容：
        生成基本的配置即可,不要使用function来动态计算值：    
        chart_visualization_config_1 = {
          //x轴字段，如果图表类型不需要则不要生成，譬如饼图
          'xAxis': <参考echart进行配置>,
          //y轴字段，如果图表类型不需要则不要生成，譬如饼图,
          'yAxis': <参考echart进行配置>,
          'title': <图表标题,参考echart进行配置,放在左边>,
          'legend':<图表标题,参考echart进行配置,放在右边>,
          'data_item_mark_point':[<用户要求特殊标记数据项，具体配置参考'# 图表可视化配置章节'>,...],
          //datasets表示一个数据集的可视化配置
          'datasets': [
            {
              //分析用户问题，设置图表类别柱状图(bar) or 饼状图(pie) or 折线图(line) or 面积图(area) or 玫瑰图(rose) or 散点图(scatte)
              "type":<bar or pie or line>,
              //数据集
              "data":<根据图表类别参考echart进行配置>
            },
            ...
          ]
    
        }
        ...
        ...
        code_unit_dict_1["chart"]=[echart_config_1,...]
    
    
    - If there are multiple code units, each should catch exceptions but avoid rethrowing them to prevent localized errors from halting the entire program. However, if there is only a single code unit, exception catching is unnecessary.For example:
    
      try:
        unit_code_1
      except Exception as e:
        code_unit_dict_1["question"]="统计每个职员的订单数量"
        print(f'Error in code_unit_1: {e}')
      
      try:
        unit_code_2
      except Exception as e:
        code_unit_dict_2["question"]="统计每个门店的订单数量"
        print(f'Error in code_unit_2: {e}')  
      ...
      ...
    - 
    
    - Do not output any Streamlit code inside the code.
    - If the user does not specify otherwise, when dealing with decimals, retain two decimal places, such as 1.55. If it is a percentage or proportion, display it in the format of xx.xx%, for example, 20.12%.
    
    ###学习资料###
    # 以下是用户的问题是否清晰，例如以下例子：
    - 用户问:统计数量，但该提问没有明确统计什么数据，不要随意发挥给用户返回你认为的数据
    # SQL Date Handling:
    - 当db dialect是duckdb时：
    -- 如果日期字段为字符串格式，那么必须先转换为日期格式：CAST(<日期字段> AS DATE)
    -- 将日期转为'月'时使用strftime(<日期字段>,'%Y-%m')，如果日期字段为字符串，则需要先转换：strftime(CAST(<日期字段> AS DATE),'%Y-%m')
    -- 将日期转为'日'时使用strftime(<日期字段>,'%Y-%m-%d')，如果日期字段为字符串，则需要先转换：strftime(CAST(<日期字段> AS DATE,'%Y-%m-%d'))
    -- 计算昨天(1天前)使用CURRENT_DATE - INTERVAL '1 day'；计算前天(2天前)使用CURRENT_DATE - INTERVAL '2 day'
    -- 计算N天前使用CURRENT_DATE - INTERVAL '<N> day'
    # 表格可视化配置：
    - 如果用户要求根据数据比较设置某一列表格单元格特殊展示样式，譬如年龄列大于10显示红色，配置项如下：
      column_style_by_data_compare:{
        "field_name":<数据字段名称，不能为空>,
        "comparison_operators":'<比较符,包括大于(>)、小于(<)、等于(==)、最大值(max)、最小值(min)，不能为空>',
        "comparison_value":<数据字段需要比较的值，当comparison_operators为max或min时设置为空，否则必须设置值>,
        "color":'<需要设置的颜色值，不能为空>'
      }
    
    # 图表可视化配置：
    - 非常重要：在生成图表配置时不要使用function来动态计算值
    - 如果用户要求设置数据项颜色(例如对于柱状图，要求每个柱子颜色不一样，对于折线图，要求每条线颜色不一样，其他图形类似)：
      data_item_color_setting:<0 or 1，0表示要求每个数据项颜色一样，1表示要求每个数据项颜色不一样>
    - 如果用户要求特殊标记数据项最大、最小值(例如对于柱状图，要求突出数值最高的柱子为红色等):
      data_item_mark_point:{
        /**
          data是一个数组，用于定义需要标记的点，包括最大值(max)、最小值(min)、平均值(average)3种，根据问题要求可存在一个或多个，譬如同时标记最高点和最低点，标记点的schema如下：
          {
            //标记点类型，有最大值(max)、最小值(min)、平均值(average)三种
            "type": '<max or min or average，不能为空>', 
            "name":'<最大值 or 最小值 or平均值，不能为空>',
            //设置标记点的样式，例如颜色、边框等
            color: '<颜色>',
            size:<标记大小>,
            //表示标记的形状
            "symbol": <pin>
          } 
        **/
        "data":[
            标记点1,
            标记点2,
            ...
          ]
      }
    "#
  }
}  