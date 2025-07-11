package com.tencent.supersonic.sync_data.cs.service;

import com.tencent.supersonic.BaseApplication;
import com.tencent.supersonic.chat.api.pojo.request.ChatExecuteReq;
import com.tencent.supersonic.chat.api.pojo.response.QueryResult;
import com.tencent.supersonic.sync_data.common.vo.PandasAiResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * <b><code>PandasAiServiceTest</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/3 15:04
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */

public class PandasAiAgentServiceTest extends BaseApplication {
    @Autowired
    private PandasAiAgentService pandasAiAgentService;

    @Test
    public void executeForString() {
        PandasAiResponse<String> response = pandasAiAgentService.executeForString(5, 1, 1L, "统计不同状态的账号数量");
        System.out.println(response);
    }

    @Test
    public void execute() {
        ChatExecuteReq chatExecuteReq = new ChatExecuteReq();
        chatExecuteReq.setAgentId(5);
        chatExecuteReq.setChatId(1);
        chatExecuteReq.setQueryText("统计不同状态的账号数量");
        QueryResult response = pandasAiAgentService.execute(chatExecuteReq);
        System.out.println(response);
    }
}