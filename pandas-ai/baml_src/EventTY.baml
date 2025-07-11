class EventTY{
  extract_type string @description(#"
    设置为'#extract_type'的值
  "#)  
  task_id string @description(#"
    案例id，从$task_id获取
  "#) 

  netEventTy NetEventTy[]  @description(#"
    网络事件实体集合
  "#)    
  locationTy LocationTy[] @description(#"
    IP地址或小区实体集合
  "#) 
  links EventAndLocationTyRel[] @description(#"
    抽取2种关系：
    1、网络事件实体和小区实体关系，从$results[*].data[*].row[*]..通用定界[*].conclusion里面抽取，查找'小区：'后面小区名称建立关系
    2、网络事件实体和IP地址实体关系，从$results[*].data[*].row[*]..通用定界[*].conclusion里面抽取，查找'IP：'后面IP地址建立关系
  "#) 
  
}

class NetEventTy {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何小区实体和IP实体id重复
  "#)  
  n string @description(#"""
      网络事件实体名称，如果名称相同则合并为同一实体，这点非常重要，从$data.outputs.report.results[*].data[*].row[*]..通用定界[*].eventName获取
  """#) 
  @@stream.done
}
// 位置
class LocationTy {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何网络事件实体id重复
  "#)    
  t string @description(#"
    位置类型，如果抽取的是小区名称，设置为1，如果抽取的是IP地址，设置为2
  "#)
  n string @description(#"""
        小区实体名称，如果名称相同则合并为同一实体，这点非常重要，从$results[*].data[*].row[*]..通用定界[*].conclusion里面抽取，查找'小区：'后面地址类信息，例如：
           '小区：佛山南海大沥滘口东区DC-ZFH-1 9次'
           这里面'佛山南海大沥滘口东区DC-ZFH-1' 就是小区实体名称，紧跟着的'9次'表示发生在该小区的网络事件次数
        IP地址，如果IP相同则为合并为同一实体，这点非常重要，从$results[*].data[*].row[*]..通用定界[*].conclusion里面抽取，查找'IP：'后面地址类信息，例如：
           'IP：59.82.17.33 2次'
           这里面'59.82.17.33'就是IP地址，紧跟着的'2次'表示发生在该ip的网络事件次数
  """#) 
  @@stream.done
}



class EventAndLocationTyRel {
  s int @description(#"
    头部节点,设置为网络事件实体id
  "#)
  t int @description(#"
    尾部节点id,设置为小区实体或IP地址实体id
  "#)   
  c int @description(#"
    事件发生的总次数，从$results[*].data[*].row[*]..通用定界[*].count获取
  "#) 
  dc int @description(#"
    在小区或IP发生的次数，从$results[*].data[*].row[*]..通用定界[*].conclusion获取，数值紧跟在小区或IP地址的后面
  "#) 
  r string @description(#"
    事件原因归类，从$results[*].data[*].row[*]..通用定界[*].causeType获取
  "#) 
  @@stream.done
}



function GenEventTY(json:string,extract_type:string) -> EventTY { 
  client Hs_deepseek_v3_250324
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    你是一个JSON结构和图数据分析专家，擅长从JSON结构中抽取实体和实体关系信息。
    我会提供详细的JSON结构给你，你需要仔细分析JSON的结构，按照我要求的输出格式生成一个图数据结构。
    要注意，以下几点非常重要，不遵循会导致致命错误：
    1、所有实体的id必须全局唯一，这点很重要。
    2、遇到相同事件合并为一个网络事件实体
    3、遇到相同小区合并为一个小区实体
    4、遇到相同IP合并为一个IP实体
    #extract_type:{{extract_type}}      
    ###JSON###
    {{json}}
    {{ ctx.output_format }}
  "# 
}

test TestGenEventTY {
  functions [GenEventTY]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
    extract_type #"NetEventTy"#
  }
}  