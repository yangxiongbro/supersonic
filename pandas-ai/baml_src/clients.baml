client<llm> Hs_deepseek_r1 {
  provider openai-generic
  options {
    model "deepseek-r1-250120"
    base_url "https://ark.cn-beijing.volces.com/api/v3"
    api_key "8e8723a1-8032-4213-9752-748fbd9fbd70"
  }
  
}

client<llm> Hs_deepseek_v3_250324 {
  provider openai-generic
  options {
    model "deepseek-v3-250324"
    base_url "https://ark.cn-beijing.volces.com/api/v3"
    api_key "8e8723a1-8032-4213-9752-748fbd9fbd70"
  }
  
}

client<llm> Hs_deepseek_v3 {
  provider openai-generic
  options {
    model "deepseek-v3-241226"
    base_url "https://ark.cn-beijing.volces.com/api/v3"
    api_key "8e8723a1-8032-4213-9752-748fbd9fbd70"
  }
  
}

client<llm> DeepSeek_Qwen32 {
  provider openai-generic
  options {
    model "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    base_url "https://api.siliconflow.cn/v1"
    api_key "sk-dkihzhdvaowvyastvjtnhutiyyfrsntqnptbpehuvbhfytzz"
  }
}



client<llm> DeepSeekV3 {
  provider openai-generic
  options {
    model "deepseek-ai/DeepSeek-V3"
    base_url "https://api.siliconflow.cn/v1"
    api_key "sk-yfibapxotobrduqertxcvhpjykczzjikeekxcrrgsqspggkd"
  }
}

client<llm> QwenCodeV2_5 {
  provider openai-generic
  options {
    model "qwen2.5-coder-32b-instruct"
    base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key "sk-8cab883d8d964e0281cf774a552f98b4"
  }
  
}