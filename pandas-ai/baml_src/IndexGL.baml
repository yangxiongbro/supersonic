class IndexGL{
  extract_type string @description(#"
    设置为'#extract_type'的值
  "#)  
  task_id string @description(#"
    案例id，从$task_id获取
  "#) 
  indexOverview IndexOverview[] @description(#"
    指标实体，从$data[*]..指标概览详情[*]，name相同的为同一个指标实体
  "#)   
  netOverviewNodes NetOverview[] @description(#"
    网络实体集合，从$data[*]..指标概览详情[*]和驻留网络信息[*].network里面抽取，network相同的为同一个网络实体
  "#) 

  links IndexGlAndNetRel[] @description(#"
    网络实体和指标实体关系集合，从$data[*]..指标概览详情[*]抽取，注意要在同一个元素里面判断网络实体和指标实体的关系
  "#) 
}


// class IndexAndIndexTimeSliceRelation {
class IndexOverview {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何网络实体id重复
  "#)  
  n string @description(#"
    指标实体名称，如果名称相同则为同一实体，这点非常重要，从$data[*]..指标概览详情[*].name和驻留网络信息[*]里面抽取，name相同的为同一个指标实体
  "#) 
  @@stream.done
}
// class Index {
class NetOverview {
  i int @description(#"
    设置一个全局唯一整数id,不能和任何指标实体id重复
  "#)  
  n string @description(#"
    网络实体名称，如果名称相同则为同一实体，这点非常重要，从$data[*]..指标概览详情[*]和驻留网络信息[*].network里面抽取，network相同的为同一个网络实体
  "#)  
  @@stream.done
  
}

class IndexGlAndNetRel {
  s int @description(#"
    头部节点,设置为指标id
  "#)
  t int @description(#"
    尾部节点id,设置为网络实体id
  "#)
  v float @description(#"
    指标值，从$data[*]..指标概览详情[*].value和驻留网络信息[*]里面抽取
  "#)
  @@stream.done

}
 


function GenIndexGL(json:string,extract_type:string) -> IndexGL { 
  client Hs_deepseek_v3_250324
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    你是一个JSON结构和图数据分析专家，擅长从JSON结构中抽取实体和实体关系信息。
    我会提供详细的JSON结构给你，你需要仔细分析JSON的结构，按照我要求的输出格式生成一个图数据结构。
    要注意，以下几点非常重要，不遵循会导致致命错误：
    1、所有实体的id必须全局唯一
    2、遇到相同指标合并为一个指标实体
    3、遇到相同网络合并为一个网络实体
    #extract_type:{{extract_type}}
    ###JSON###
    {{json}}
    {{ ctx.output_format }}
  "# 
}

test TestGenIndexGL {
  functions [GenIndexGL]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
    extract_type #"indexOverview"#
  }
}  