class EventAll{
  eventKS EventKS 
  eventSB EventSB 
  eventTY EventTY
}




function GenEventAll(json:string) -> EventAll { 
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

test TestGenEventAll {
  functions [GenEventAll]
  args {
    json #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息  
    "#
  }
}  