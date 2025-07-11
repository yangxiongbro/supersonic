from typing import *
import json
import pandas as pd
def table_vis_render(table:any,data:dict,config:dict):
    if "column_style_by_data_compare" in config :
        column_style_by_data_compare(table,data,config["column_style_by_data_compare"])
def column_style_by_data_compare(table:any,data:dict,config_info:Union[list,dict]):
    """
    - 根据数据比较设置某一列表格单元格特殊展示样式，譬如年龄列大于10显示红色，配置项如下： 
    column_style_by_data_compare:[{
        "field_name":<数据字段名称>,
        "comparison_operators":<比较符,包括大于(>)、小于(<)、等于(=)、最大值(max)、最小值(min)>,
        "comparison_value":<数据字段需要比较的值>
        "color":<需要设置的颜色值>
    }]
    """    
    config_arr=[]
    if isinstance(config_info,dict):
        config_arr.append(config_info)
    else:
        config_arr=config_info
    for config in config_arr:
        if 'field_name' not in config or 'comparison_operators' not in config or 'comparison_value' not in config:
            continue
        field_name=config["field_name"]
        comparison_operators=config["comparison_operators"]
        comparison_value=config["comparison_value"]
        color=config["color"]    
        if comparison_operators=='max':
            comparison_operators="=="
            comparison_value = max(row[field_name] for row in data)

        elif comparison_operators=='min':
            comparison_operators="=="
            comparison_value = min(row[field_name] for row in data)      

        slot=f'''
        <q-td key="{field_name}" :props="props">
            <q-badge :color="props.value {comparison_operators} {comparison_value} ? '{color}' : 'black'">
        '''
        slot+='{{ props.value }}'
                
        slot+='</q-badge>'
        slot+='</q-td>'       

        table.add_slot(f'body-cell-{field_name}', slot)

'''
{
      'xAxis_field': '<x轴字段，如果图表类型不需要则不要生成，譬如饼图>',
      'yAxis_field': '<y轴字段，如果图表类型不需要则不要生成，譬如饼图>',
      'title': '<图表标题>',
      'data_item_mark_point':[<用户要求特殊标记数据项，具体配置参考'# 图表可视化配置章节'>,...],
      //datasets表示一个数据集的可视化配置
      'datasets': [
        {
          //图表类别
          "type":<bar(柱状图) or pie(饼图) or line(折线图) or area(面积图) or rose(玫瑰图) or scatter(散点图)>,
          //数据集
          "data":<df_1>
        },
        ...
      ]

    }
'''

def render_chart_default(config:dict,data:pd.DataFrame)->Dict:
    options={
        'legend':{
            'top':'top'
        },
        'toolbox': {
            'show': True,
            'feature': {
                'mark': { 'show': True },
                'dataView': { 'show': True, 'readOnly': False },
                'restore': { 'show': True },
                'saveAsImage': { 'show': True }
            }
        }
    }
    if ('dimensions' not in config) or ('metric' not in config):
        return None
    else:
        if config['dimensions'] is None or len(config['dimensions']) ==0:
            return None
        if config['metric'] is None:
            return None

    dimensions=config['dimensions']
    metric=config['dimensions']
    type=config['user_chart_type']

    metric=config['metric']
    serie_arr=None
    if type=="rose":#玫瑰图默认样式   
        serie_conf={}     
        serie_conf['type']='pie'
        serie_conf['roseType']='area'
        serie_conf["radius"]=[20,"70%"]
        serie_conf['itemStyle']={}            
        serie_conf['itemStyle']["borderRadius"]=5     
        #处理数据
        # 判断有多少个维度
        serie_arr=_create_dim_pie_serie_data(data,serie_conf,dimensions,metric)   
    elif type=='pie':#一般饼图
        serie_conf={}   
        serie_conf['type']='pie'
        serie_conf['radius']='50%'  
        #处理数据
        # 判断有多少个维度
        serie_arr=_create_dim_pie_serie_data(data,serie_conf,dimensions,metric)           
    elif type=="donut":#环形图默认样式
        serie_conf=  {
            'type': 'pie',
            'radius': ['40%', '70%'],
            'avoidLabelOverlap': False,
            'itemStyle': {
                'borderRadius': 4,
                'borderColor': '#fff',
                'borderWidth': 2
            },
            'label': {
                'show': False,
                'position': 'center'
            },
            'emphasis': {
                'label': {
                'show': True,
                'fontSize': 12,
                'fontWeight': 'bold'
                }
            },
            'labelLine': {
                'show':False
            }
        }
        serie_arr=_create_dim_pie_serie_data(data,serie_conf,dimensions,metric) 
    elif type=="line":#线形图默认样式

        xAxisData=_create_xAxis_data(data,dimensions)
        options['xAxis']={
            'type': 'category',
            'data': xAxisData
        }
        options['yAxis']={
            'type': 'value'
        },
        serie_conf={
                    'type': 'line',
                    'symbol': 'triangle',
                    'symbolSize': 20,
                    'lineStyle': {
                        'color': '#5470C6',
                        'width': 4,
                        'type': 'dashed'
                    },
                    'itemStyle': {
                        'borderWidth': 3,
                        'borderColor': '#EE6666',
                        'color': 'yellow'
                    }
                    }
        serie_arr=_create_dim_line_serie_data(data,serie_conf,dimensions,metric) 
    elif type=="area":#面积默认样式
        xAxisData=_create_xAxis_data(data,dimensions)
        options['xAxis']={
            'type': 'category',
            'data': xAxisData
        }
        options['yAxis']={
            'type': 'value'
        },        
        serie_conf={}
        serie_conf['type']='line'
        serie_conf['areaStyle']={}
        serie_arr=_create_dim_line_serie_data(data,serie_conf,dimensions,metric) 
    elif type=="scatter":
        serie_conf={}
        serie_conf['type']='scatter'        
    elif type=="bar":
        xAxisData=_create_xAxis_data(data,dimensions)
        options['xAxis']={
            'type': 'category',
            'data': xAxisData
        }
        options['yAxis']={
            'type': 'value'
        },        
        serie_conf={}
        serie_conf['type']='bar'           
        options["tooltip"]={
            "trigger": 'axis',
            "axisPointer": {
            "type": 'shadow'
            }
        }         
        serie_arr=_create_dim_bar_serie_data(data,serie_conf,dimensions,metric)    

    # if "data_item_mark_point" in config:
    #     # serie['markPoint']=config['data_item_mark_point']
    #     if 'data' in config['data_item_mark_point'] :
    #         for mark in config['data_item_mark_point']['data']:
    #             if 'color' in mark:
    #                 mark['itemStyle']={'color':mark['color']}
    #     serie['markPoint']=config['data_item_mark_point']

    if serie_arr is None:
        return None
    options['series']=serie_arr

    print(json.dumps(options,ensure_ascii=False,indent=4))

    return options

def _create_xAxis_data(data:pd.DataFrame,dimensions:list)->list:
    xAxis = data.apply(lambda row: '_'.join([str(row[col]) for col in dimensions]), axis=1).tolist()  
    print(isinstance(xAxis,list))
    print(isinstance(xAxis,pd.DataFrame))
    return xAxis  

def _create_dim_pie_serie_data(data:pd.DataFrame,serie_conf:dict,dimensions:list,metric:str)->list:
    serie_arr=[]
    if len(dimensions)==1:
        #获取维度值
        # demValue=data[dimensions[0]]
        dim=dimensions[0]
        serie={}       
        serie['data']=data.apply(lambda row: {'name': row[dim], 'value': row[metric]}, axis=1).tolist()
        merged_json = {**serie_conf, **serie}
        serie_arr.append(merged_json)

    elif len(dimensions)>1:
        print()
    return serie_arr
def _create_dim_bar_serie_data(data:pd.DataFrame,serie_conf:dict,dimensions:list,metric:str)->list:
    serie_arr=[]
    if len(dimensions)==1:
        #获取维度值
        # demValue=data[dimensions[0]]
        dim=dimensions[0]
        serie={}       
        serie['data']=data.apply(lambda row: row[metric], axis=1).tolist()
        merged_json = {**serie_conf, **serie}
        serie_arr.append(merged_json)

    elif len(dimensions)>1:
        print()
    return serie_arr

def _create_dim_line_serie_data(data:pd.DataFrame,serie_conf:dict,dimensions:list,metric:str)->list:
    serie_arr=[]
    if len(dimensions)==1:
        #获取维度值
        # demValue=data[dimensions[0]]
        dim=dimensions[0]
        serie={}       
        serie['data']=data.apply(lambda row: row[metric], axis=1).tolist()
        merged_json = {**serie_conf, **serie}
        serie_arr.append(merged_json)

    elif len(dimensions)>1:
        print()
    return serie_arr
  
    

def chart_vis_render(config:dict,vis_config:dict):
    try:
        if "data_item_mark_point" in vis_config:
            data_item_mark_point(config,vis_config["data_item_mark_point"])
        if "data_item_color_setting" in vis_config:
            data_item_color_setting(config,vis_config["data_item_color_setting"])
        
        print("echart config:"+json.dumps(config, indent=4, ensure_ascii=False))
    except Exception as e:
        print(e)
        

def data_item_mark_point(config:dict,vis_config:int):
    """
     'markPoint': {
            'data': [
                {'type': 'max', 'name': '最大值', 'itemStyle': {'color': 'red'}}
            ]
        }
    """
    for serie in config["series"]:
        if serie["type"]=='bar' or serie["type"]=='line':
            serie["markPoint"]=vis_config

def data_item_color_setting(config:dict,flag:bool):
    if flag==1:
        config["series"][0]["colorBy"]="data"