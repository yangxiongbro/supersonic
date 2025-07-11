class IndexYW{
  extract_type string @description(#"
    设置为'#extract_type'的值
  "#)
  task_id string @description(#"
    案例id，从$task_id获取
  "#) 

  indexOfBus IndexOfBus[]  @description(#"
    指标实体集合
  "#)    
  bus Bus[] @description(#"
    业务小类实体集合
  "#) 
  links IndexAndBusRel[] @description(#"
    指标实体和业务小类实体关系集合，从$data.outputs.report.results[*].data[*].row[*]..用户指标集中性分析[*]数组中抽取，并且必须在以'业务小类维度'开头的数组元素里面抽取，注意要在同一个数组元素里面判断指标实体和业务小类实体的关系
  "#)   
}
 

class IndexOfBus {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何业务实体id重复
  "#)  
  n string @description(#"
    指标实体名称，如果名称相同则为同一实体，这点非常重要，从$data.outputs.report.results[*].data[*].row[*]..用户指标集中性分析[*]数组中抽取，并且必须在以'业务小类维度'开头和包含'有集中性'的数组元素里面抽取，指标实体名称在'业务小类维度，指标：'后面，例如以下数组元素：
    '业务小类维度，指标：TCP建链平均时延(ms)，无集中性，集中度为0.5000，低于阈值0.5000'
    这里面'TCP建链平均时延(ms)'中'TCP建链平均时延'就是指标实体名称,,最右边'(ms)'是单位，其他指标也一样，切记不要附加到指标名称后面
  "#) 
  @@stream.done
}
class Bus {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何指标实体id重复
  "#) 
  n string @description(#"
    业务小类实体名称，如果名称相同则为同一实体，这点非常重要，从$data.outputs.report.results[*].data[*].row[*]..用户指标集中性分析[*]数组中抽取，并且必须在以'业务小类维度'开头和包含'有集中性'的数组元素里面抽取，查找'、指标值'前面的业务小类实体名称，例如以下数组元素：
      '业务小类维度，指标：TCP二三次握手平均时延(ms)，有集中性，集中度为0.9574，高于阈值0.6000\n\t苹果iCloud、指标值：129.07, 总时延：1936.09, 成功次数：15.00, 影响度：-0.0362\n\t73001、指标值：140.71, 总时延：5628.27, 成功次数：40.00'
      这里面'苹果iCloud','73001'就是业务小类实体名称
  "#)  
  @@stream.done
}

class IndexAndBusRel {
  s int @description(#"
    头部节点,设置为指标实体id
  "#)
  t int @description(#"
    尾部节点id,设置为业务小类实体id
  "#)  
  v string @description(#"
    指标值，$$data.outputs.report.results[*].data[*].row[*]..用户指标集中性分析[*]..业务小类维度..指标值里面抽取，例如：
    '苹果iCloud、指标值：129.07, 总时延：1936.09, 成功次数：15.00, 影响度：-0.0362'
    这里面129.07是指标值，1936.09是指标分子，15.00是指标分母
  "#)
  j string @description(#"
    指标是否有集中性，$$data.outputs.report.results[*].data[*].row[*]..用户指标集中性分析[*]提取"有集中性"和"无集中性"，有集中性设置为1，无集中性设置为0
  "#)    
  z string @description(#"
    指标分子
  "#)   
  m string @description(#"
    指标分母
  "#)   
  @@stream.done
}
 


function GenIndexYW(json:string,extract_type:string) -> IndexYW { 
  client Hs_deepseek_v3_250324
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    你是一个JSON结构和图数据分析专家，擅长从JSON结构中抽取实体和实体关系信息。
    我会提供详细的JSON结构给你，你需要仔细分析JSON的结构，按照我要求的输出格式生成一个图数据结构。
    要注意，以下几点非常重要，不遵循会导致致命错误：
    1、所有实体的id必须全局唯一
    2、遇到相同指标合并为一个指标实体
    3、遇到相同业务小类合并为一个业务小类实体
    #extract_type:{{extract_type}}    
    {{IndexList()}}
    ###JSON###
    {{json}}
    {{ ctx.output_format }}
  "# 
}

test TestIndexYW {
  functions [GenIndexYW]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
    extract_type #"indexOfBus"#
  }
}  