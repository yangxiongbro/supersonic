class Agents{
    chatAgent ChatAgent[] @description(#"
    推荐的Agent集合，没有合适的则设置为空
  "#)
    summary string @description(#"
    总结推荐的信息
  "#)
} 
class ChatAgent {
  name string @description(#"
    Agent名称
  "#)
  question string @description(#"
    对应的问题
  "#)
  reason string @description(#"
    推荐的理由
  "#)
  dependent string @description(#"
    需要依赖哪个Agent返回的数据，设置Agent的名称
  "#)
}

function Recommendation(user_query:string,agent_info: string) -> Agents {
  client DeepSeekV3
  prompt #"    
    你是一个专业的工作调度员，你拥有一个Agent团队，每个Agent都有自己的职责和技能。
    你很擅长对用户的问题进行分解并推荐合适的Agent解答用户的问题，Agent的职责和技能描述是你推荐的重要依据。
    如果用户的问题和Agent的职责和技能关系不大，则返回空chatAgent集合,只需要在summary返回信息即可。
    如果用户问到你的团队信息，那么不必返回chatAgent集合，只需要在summary返回信息即可。
        
    Agent的信息:
    ---
    {{agent_info}}
    ---

    {{ _.role("user") }}
    QUESTION: {{ user_query }}
    {{ ctx.output_format }}
  "#
}

test RecommendAgent {
  functions [Recommendation]
  args {
    agent_info #"
      ---Agent1---
      name: 缺陷分析助手
      skill: 分析缺陷数据

      ---Agent2---
      name: 员工信息助手
      skill: 查询员工的详细信息
    "#
    user_query #"
        统计开发人员的缺陷数量并且列出开发人员的详细信息
    "#
  }
}  