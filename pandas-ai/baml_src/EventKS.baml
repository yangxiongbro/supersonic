class EventKS{
  extract_type string @description(#"
    设置为'#extract_type'的值
  "#)  
  task_id string @description(#"
    案例id，从$task_id获取
  "#) 

  netEvent NetEvent[]  @description(#"
    网络事件实体集合
  "#)    
  location Location[] @description(#"
    IP地址或小区实体集合
  "#) 
  links NetEventAndLocationRel[] @description(#"
    抽取2种关系：
    1、网络事件实体和小区实体关系，从$results[*].data[*].row[*]..快速定界[*].conclusion里面抽取，查找'小区：'后面小区名称建立关系
    2、网络事件实体和IP地址实体关系，从$results[*].data[*].row[*]..快速定界[*].conclusion里面抽取，查找'IP：'后面IP地址建立关系
  "#) 
}

class NetEvent {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何小区实体和IP实体id重复
  "#)  
  n string @description(#"""
      网络事件实体名称，如果名称相同则为同一实体，这点非常重要，从$data.outputs.report.results[*].data[*].row[*]..快速定界[*].sceneName获取
  """#) 
  @@stream.done
}
// 位置
class Location {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何网络事件实体id重复
  "#)    
  t string @description(#"
    位置类型，如果抽取的是小区名称，设置为1，如果抽取的是IP地址，设置为2
  "#)
  n string @description(#"""
        小区实体名称，如果名称相同则为同一实体，这点非常重要，从$results[*].data[*].row[*]..快速定界[*].conclusion里面抽取，查找'小区：'后面地址类信息，例如：
           '小区：佛山南海大沥滘口东区DC-ZFH-1 9次、佛山南海大沥滘口东区DC-ZFH-2 5次、佛山南海大沥上漖村南新区南二巷DC-KFH-1 3次；'
           这里面'佛山南海大沥滘口东区DC-ZFH-1' 和 '佛山南海大沥滘口东区DC-ZFH-2' 和 '佛山南海大沥上漖村南新区南二巷DC-KFH-1'就是小区实体名称
        IP地址，如果IP相同则为同一IP地址实体，这点非常重要，从$results[*].data[*].row[*]..conclusion里面抽取，查找'IP：'后面地址类信息，例如：
           'IP：59.82.17.33 2次，2403:300:A0A:F000:0:0:0:7 3次'
           这里面'59.82.17.33'和'2403:300:A42:C0A:0:0:0:8'就是IP地址
  """#) 
  @@stream.done
}


// 事件时间切片
class NetEventAndLocationRel {
  s int @description(#"
    头部节点,设置为网络事件实体id
  "#)
  t int @description(#"
    尾部节点id,设置为小区实体或IP地址实体id
  "#)   
  c int @description(#"
    事件发生的次数，从$results[*].data[*].row[*]..快速定界[*].conclusion获取
  "#) 
  r string @description(#"
    事件原因归类，从$results[*].data[*].row[*]..快速定界[*].causeType获取
  "#) 
  d string @description(#"
    事件发生日期区间，从$results[*].data[*].row[*]..快速定界[*].conclusion获取时间区间，例如:
    "频繁互操作：2025-04-06 01:23:44.502 - 2025-04-06 01:24:15.508，发生频繁互操作5次。小区：惠州西区亲水湾【西区邮政2】D-HLW-1、未知小区51626057729"
    这里面'2025-04-06 01:23:44.502 - 2025-04-06 01:24:15.508'就是事件发生日期区间
  "#)   
  @@stream.done
}



function GenEventKS(json:string,extract_type:string) -> EventKS { 
  client Hs_deepseek_v3_250324
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    你是一个JSON结构和图数据分析专家，擅长从JSON结构中抽取实体和实体关系信息。
    我会提供详细的JSON结构给你，你需要仔细分析JSON的结构，按照我要求的输出格式生成一个图数据结构。
    要注意，以下几点非常重要，不遵循会导致致命错误：
    1、所有实体的id必须全局唯一
    2、遇到相同事件合并为一个网络事件实体
    3、遇到相同小区合并为一个小区实体
    4、遇到相同IP合并为一个IP实体
    #extract_type:{{extract_type}}    
    ###JSON###
    {{json}}
    {{ ctx.output_format }}
  "# 
}

test TestGenEventKS {
  functions [GenEventKS]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
    extract_type #"netEvent"#
  }
}  