package com.tencent.supersonic.sync_data.cs.service;

import com.tencent.supersonic.chat.api.pojo.request.ChatExecuteReq;
import com.tencent.supersonic.chat.api.pojo.response.QueryResult;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.vo.PandasAiResponse;

import java.util.List;

/**
 * <b><code>PandasAiService</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/3 11:54
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public interface PandasAiAgentService {

    /**
     * @description: 更新助手
     * @param: agentIdList
     * @return: Integer
     * @throws
     * @author yang xiong
     * @date 2025/6/9 11:56
     **/
    Integer updateAgent(List<Integer> agentIdList) throws BaseException;

    /**
     * @description: 删除助手
     * @param: agentIdList
     * @return: Integer
     * @throws
     * @author yang xiong
     * @date 2025/6/9 11:56
     **/
    Integer deleteAgent(List<Integer> agentIdList) throws BaseException;

    /**
     * @description: 请求助手
     * @param: agentId
     * @param: chatId
     * @param: queryId
     * @param: queryText
     * @return: PandasAiChatResponse
     * @throws
     * @author yang xiong
     * @date 2025/6/5 14:42
     **/
    PandasAiResponse<String> executeForString(Integer agentId, Integer chatId, Long queryId, String queryText);

    /**
     * @description: 请求助手
     * @param: chatExecuteReq
     * @return: QueryResult
     * @throws
     * @author yang xiong
     * @date 2025/6/6 15:58
     **/
    QueryResult execute(ChatExecuteReq chatExecuteReq);

    /**
     * @description: 获取引用该大模型的助手id
     * @param: chatModelId
     * @return: List
     * @throws
     * @author yang xiong
     * @date 2025/6/21 16:20
     **/
    List<Integer> listChatModelAgentId(Integer chatModelId);

    /**
     * @description: 根据术语id获取数据集id
     * @param: termIdList
     * @return: List
     * @throws
     * @author yang xiong
     * @date 2025/6/21 16:21
     **/
    List<Long> listDataSetIdByTermId(List<Long> termIdList);

    /**
     * @description: 获取引用该数据集的助手id
     * @param: dataSetIdList
     * @return: List
     * @throws
     * @author yang xiong
     * @date 2025/6/21 16:21
     **/
    List<Integer> getAgentIdList(List<Long> dataSetIdList);
}
