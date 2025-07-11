class IndexGL4g{
  task_id string @description(#"
    案例id，从$task_id获取
  "#) 

  indexOverviewTriple4g IndexOverviewTriple4g[] @description(#"
    指标和指标网络类型的三元组集合，从以下地方抽取：
    1、从$data[*]..指标概览详情[*]数组抽取多个指标实体,只抽取network是4G的实体
    2、从$data[*]..驻留网络信息[*]数组抽取多个指标实体,只抽取network是4G的实体
      驻留网络信息中指标输出使用中文名称，指标对应中文名如下：{"dlData(MB)":"HTTP流量", "dlDataRatio(%)":"HTTP流量占比","resideTimeRatio(%)":"驻留时长占比","resideTime(s)":"驻留时长"}
  "#)    
}

// class IndexAndIndexTimeSliceTriple {
class IndexOverviewTriple4g {
  h IndexOverview4g  @description(#"
    头部节点,设置为指标实体
  "#) 
  t NetOverview4g  @description(#"
    尾部节点,设置网络实体
  "#) 
  r IndexGlAndNetRel4g @description(#"
      指标和指标网络的关系
  "#) 
  @@stream.done
}
// class IndexAndIndexTimeSliceRelation {
class IndexOverview4g{
  tp string @description(#"
    设置为index
  "#)  
  n string @description(#"
    指标名称，从$data[*]..指标概览详情[*].name和驻留网络信息[*]里面抽取
  "#) 
}
// class Index {
class NetOverview4g {
  tp string @description(#"
    设置为n
  "#)
  n string @description(#"
    所属网络，从$data[*]..指标概览详情[*]和驻留网络信息[*]
  "#)  
  
}

class IndexGlAndNetRel4g {
  v string @description(#"
    指标值，从$data[*]..指标概览详情[*].value和驻留网络信息[*]里面抽取
  "#)
  n string @description(#"
    设置值"BELONG_TO"，表示指标归属的网络
  "#) 

}
 


function GenIndexGL4g(json:string) -> IndexGL4g { 
  client Hs_deepseek_v3_250324
  // client Hs_deepseek_r1
  // client QwenCodeV2_5

  prompt #"    
    你是一个JSON结构和图数据分析专家，擅长从JSON结构中抽取实体和实体关系信息。
    我会提供详细的JSON结构给你，你需要仔细分析JSON的结构，按照我要求的输出格式生成一个图数据结构。
    ###JSON###
    {{json}}
    {{ ctx.output_format }}
  "# 
}

test TestGenIndexGL4g {
  functions [GenIndexGL]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
  }
}  