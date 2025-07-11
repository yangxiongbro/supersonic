package com.tencent.supersonic.sync_data.cs.service.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.tencent.supersonic.chat.api.pojo.request.ChatExecuteReq;
import com.tencent.supersonic.common.pojo.QueryColumn;
import com.tencent.supersonic.common.util.JsonUtil;
import com.tencent.supersonic.headless.api.pojo.SemanticParseInfo;
import com.tencent.supersonic.headless.api.pojo.SqlInfo;
import com.tencent.supersonic.headless.api.pojo.response.QueryState;
import com.tencent.supersonic.sync_data.common.config.properties.PandasAiInfo;
import com.tencent.supersonic.sync_data.common.constants.TrinoConstants;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.exception.business.BusinessExceptionAssertResponseEnum;
import com.tencent.supersonic.sync_data.common.vo.AgentVO;
import com.tencent.supersonic.sync_data.common.vo.PandasAiResponse;
import com.tencent.supersonic.sync_data.cs.mapper.PandasAiAgentMapper;
import com.tencent.supersonic.sync_data.cs.service.PandasAiAgentService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;
import com.tencent.supersonic.chat.api.pojo.response.QueryResult;

import java.util.*;
import java.util.stream.Collectors;

/**
 * <b><code>PandasAiServiceImpl</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/3 11:54
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Slf4j
@Service
public class PandasAiAgentServiceImpl implements PandasAiAgentService {

    private PandasAiAgentMapper pandasAiAgentMapper;

    private RestTemplate restTemplateWithLogging;

    private PandasAiInfo pandasAiInfo;

    private ObjectMapper mapper;

    public PandasAiAgentServiceImpl(PandasAiAgentMapper pandasAiAgentMapper, RestTemplate restTemplateWithLogging, PandasAiInfo pandasAiInfo, ObjectMapper mapper) {
        this.pandasAiAgentMapper = pandasAiAgentMapper;
        this.restTemplateWithLogging = restTemplateWithLogging;
        this.pandasAiInfo = pandasAiInfo;
        this.mapper = mapper;
    }

    public Integer updateAgent(List<Integer> agentIdList) throws BaseException {
        return deleteAgent(agentIdList);
    }

    public Integer deleteAgent(List<Integer> agentIdList) throws BaseException {
        if(CollectionUtils.isEmpty(agentIdList)) {
            return 0;
        }
        ResponseEntity<PandasAiResponse<Integer>> responseEntity = restTemplateWithLogging.exchange(
                pandasAiInfo.getUrl()+"/sync_data/delete_agent",
                HttpMethod.POST,
                new HttpEntity<>(Collections.singletonMap("agentIdList", agentIdList), TrinoConstants.POST_HEADERS),
                new ParameterizedTypeReference<>() {});
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertNotNull(responseEntity.getBody(), "空的响应");
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertTrue(200 == responseEntity.getBody().getCode(), responseEntity.getBody().getMsg());
        return responseEntity.getBody().getData();
    }

    public PandasAiResponse<String> executeForString(Integer agentId, Integer chatId, Long queryId, String queryText) {
        Map<String, Object> body = new HashMap<>();
        body.put("agentId", agentId);
        body.put("chatId", chatId);
        body.put("queryId", queryId);
        body.put("queryText", queryText);

//        ResponseEntity<PandasAiResponse<List<PandasAiChatResponse>>> responseEntity = restTemplateWithLogging.exchange(
//                pandasAiInfo.getUrl()+"/agent/execute",
//                HttpMethod.POST,
//                request,
//                new ParameterizedTypeReference<>() {}
//        );
        PandasAiResponse<String> pandasAiResponse = new PandasAiResponse<>();
        try {
            ResponseEntity<String> responseEntity = restTemplateWithLogging.exchange(
                    pandasAiInfo.getUrl()+"/agent/execute",
                    HttpMethod.POST,
                    new HttpEntity<>(body, TrinoConstants.CONTENT_JSON_ACCEPT_TEXT_HEADERS),
                    String.class
            );
            JsonNode rootNode = mapper.readTree(responseEntity.getBody());
            if(!rootNode.isNull()){
                if(!rootNode.get("code").isNull()){
                    pandasAiResponse.setCode(rootNode.get("code").asInt());
                }
                if(!rootNode.get("msg").isNull()){
                    pandasAiResponse.setMsg(rootNode.get("msg").toString());
                }
                if(!rootNode.get("data").isNull()){
                    pandasAiResponse.setData(rootNode.get("data").toString());
                }
            }
        } catch (Exception e) {
            log.error("executeForString Exception:{}", e);
            pandasAiResponse.setCode(HttpStatus.INTERNAL_SERVER_ERROR.value());
            pandasAiResponse.setMsg(e.getMessage());
        }
        return pandasAiResponse;
    }

    public QueryResult execute(ChatExecuteReq chatExecuteReq){
        QueryResult queryResult = new QueryResult();
        queryResult.setQueryMode("LLM_S2SQL");
        queryResult.setQueryState(QueryState.EMPTY);
        long startTime = System.currentTimeMillis();
        try{
            PandasAiResponse<String> response = executeForString(chatExecuteReq.getAgentId(), chatExecuteReq.getChatId(), chatExecuteReq.getQueryId(), chatExecuteReq.getQueryText());
            if(200 == response.getCode()){
                JsonNode rootNode = mapper.readTree(response.getData());
                JsonNode firstData = rootNode.path(0);
                List<Map<String, Object>> resultDataList = null;
                if(!firstData.path("data").isEmpty()){
                    resultDataList = mapper.readValue(firstData.path("data").toString(), new TypeReference<>() {});
                }
                if(CollectionUtils.isEmpty(resultDataList)){
                    resultDataList = TrinoConstants.PANDAS_AI_NOT_DATA_RESPONSE;
                }
                queryResult.setQueryResults(resultDataList);
                String sql = firstData.path("sql").toString();
                SqlInfo sqlInfo = new SqlInfo();
                sqlInfo.setQuerySQL(sql);
                SemanticParseInfo chatContext = new SemanticParseInfo();
                chatContext.setSqlInfo(sqlInfo);
                queryResult.setChatContext(chatContext);
                queryResult.setTextSummary(firstData.path("explain").toString() + "。sql：" + sql);
                queryResult.setQueryState(QueryState.SUCCESS);
                queryResult.setQueryColumns(resultDataList.stream()
                        .flatMap(map -> map.keySet().stream()).distinct().sorted()
                        .map(key -> new QueryColumn(key, null, key)).toList()
                );
            } else {
                queryResult.setQueryState(QueryState.SEARCH_EXCEPTION);
                queryResult.setErrorMsg(response.getMsg());
            }
        } catch (Exception e) {
            log.warn("查询 pandas-ai 失败：{}", e);
            queryResult.setQueryState(QueryState.SEARCH_EXCEPTION);
            queryResult.setErrorMsg(e.getMessage());
        }
        queryResult.setQueryTimeCost(System.currentTimeMillis() - startTime);
        return queryResult;
    }


    public List<Integer> listChatModelAgentId(Integer chatModelId) {
        return pandasAiAgentMapper.listChatModelAgentId(chatModelId);
    }

    public List<Long> listDataSetIdByTermId(List<Long> termIdList) {
        if(CollectionUtils.isEmpty(termIdList)){
            return Collections.emptyList();
        }
        return pandasAiAgentMapper.listDataSetIdByTermId(termIdList);
    }

    public List<Integer> getAgentIdList(List<Long> dataSetIdList){
        if(CollectionUtils.isEmpty(dataSetIdList)){
            return Collections.emptyList();
        }
        return pandasAiAgentMapper.listDateSetAgent().stream()
                .filter(agentVO -> {
                    if(!StringUtils.hasText(agentVO.getToolConfig())){
                        return false;
                    }
                    AgentVO.ToolConfig toolConfig = JsonUtil.toObject(agentVO.getToolConfig(), AgentVO.ToolConfig.class);
                    if(CollectionUtils.isEmpty(toolConfig.getTools())){
                        return false;
                    }
                    for(AgentVO.Tool tool: toolConfig.getTools()){
                        if(!CollectionUtils.isEmpty(tool.getDataSetIds()) && !Collections.disjoint(dataSetIdList, tool.getDataSetIds())){
                            return true;
                        }
                    }
                    return false;
                }).
                map(AgentVO::getId).collect(Collectors.toList());
    }


}
