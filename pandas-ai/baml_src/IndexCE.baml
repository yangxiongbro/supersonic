class IndexCE{
  extract_type string @description(#"
    设置为'#extract_type'的值
  "#)
  task_id string @description(#"
    案例id，从$task_id获取
  "#) 
  indexOfCell IndexOfCell[]  @description(#"
    指标实体集合
  "#)    
  cell Cell[] @description(#"
    小区实体集合
  "#) 
  links IndexAndCellRel[] @description(#"
    指标实体和小区实体关系集合，从$data.outputs.report.results[*].data[*].row[*]..用户指标集中性分析[*]数组中抽取，并且必须在以'小区维度'开头的数组元素里面抽取，注意要在同一个数组元素里面判断指标实体和小区实体的关系
  "#)   

}

class IndexOfCell {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何小区实体id重复
  "#)   
  n string @description(#"
    指标实体名称，如果名称相同则为同一实体，这点非常重要，从$results[*].data[*].row[*]..用户指标集中性分析[*]数组中抽取，并且必须在以'小区维度'开头和包含'有集中性'的数组元素里面抽取，指标实体名称在'小区维度，指标：'后面，例如以下数组元素：
    '小区维度，指标：TCP建链平均时延(ms)，无集中性，集中度为0.5000，低于阈值0.5000'
    这里面'TCP建链平均时延(ms)'中'TCP建链平均时延'就是指标实体名称,最右边'(ms)'是单位，其他指标也一样，切记不要附加到指标名称后面
  "#) 
  @@stream.done
}
class Cell {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何指标实体id重复
  "#)   
  n string @description(#"
    小区实体名称，如果名称相同则为同一实体，这点非常重要，从$results[*].data[*].row[*]..用户指标集中性分析[*]数组中抽取，并且必须在以'小区维度'开头和包含'有集中性'的数组元素里面抽取，查找'、指标值'前面的小区实体名称，例如以下数组元素：
    '小区维度，指标：附着/注册平均时延(ms)，有集中性，集中度为0.8000，高于阈值0.6000\n\t深圳松岗捷创D-ZRH-3、指标值：122.88, 总时延：3932.00, 成功次数：32.00, 影响度：-0.0956'
    这里面'深圳松岗捷创D-ZRH-3'就是小区实体名称
  "#)  
  @@stream.done
}

class IndexAndCellRel {
  s int @description(#"
    头部节点,设置为指标实体id
  "#)
  t int @description(#"
    尾部节点id,设置为小区实体id
  "#)     
  v string @description(#"
    指标值，$results[*].data[*].row[*]..用户指标集中性分析[*]..小区名称后面的'指标值:'里面抽取，例如：
    '深圳松岗捷创D-ZRH-3、指标值：122.88, 总时延：3932.00, 成功次数：32.00, 影响度：-0.0956'
    这里面122.88是指标值，3932.00是指标分子，32.00是指标分母
  "#)
  j string @description(#"
    指标是否有集中性，$results[*].data[*].row[*]..用户指标集中性分析[*]..提取小区维度的指标有无集中性，'有集中性'设置为1，'无集中性'设置为0
  "#)    
  z string @description(#"
    指标分子
  "#)   
  m string @description(#"
    指标分母
  "#)   
  @@stream.done
}
 


function GenIndexCE(json:string,extract_type:string) -> IndexCE { 
  client Hs_deepseek_v3_250324
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    你是一个JSON结构和图数据分析专家，擅长从JSON结构中抽取实体和实体关系信息。
    我会提供详细的JSON结构给你，你需要仔细分析JSON的结构，按照我要求的输出格式生成一个图数据结构。
    要注意，以下几点非常重要，不遵循会导致致命错误：
    1、所有实体的id必须全局唯一
    2、遇到相同指标合并为一个指标实体
    3、遇到相同小区合并为一个小区实体

    #extract_type:{{extract_type}}
    {{IndexList()}}
    ###JSON###
    {{json}}
    {{ ctx.output_format }}
  "# 
}

test TestIndexCE {
  functions [GenIndexCE]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
    extract_type #"indexOfCell"#
  }
}  