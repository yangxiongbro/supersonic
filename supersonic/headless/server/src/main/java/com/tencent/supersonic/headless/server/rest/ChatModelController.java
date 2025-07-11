package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.config.ChatModel;
import com.tencent.supersonic.common.pojo.ChatApp;
import com.tencent.supersonic.common.pojo.ChatModelConfig;
import com.tencent.supersonic.common.pojo.ChatModelParameters;
import com.tencent.supersonic.common.pojo.Parameter;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.common.service.ChatModelService;
import com.tencent.supersonic.headless.server.utils.ModelConfigHelper;
import com.tencent.supersonic.sync_data.common.constants.TrinoConstants;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.cs.service.PandasAiAgentService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping({"/api/chat/model", "/openapi/chat/model"})
public class ChatModelController {
    @Autowired
    private ChatModelService chatModelService;
    @Autowired
    private PandasAiAgentService pandasAiAgentService;

    @PostMapping
    public ChatModel createModel(@RequestBody ChatModel model,
            HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        return chatModelService.createChatModel(model, user);
    }

    @PutMapping
    @Transactional(rollbackFor = Exception.class)
    public ChatModel updateModel(@RequestBody ChatModel model,
            HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) throws BaseException {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        ChatModel resp = chatModelService.updateChatModel(model, user);
        pandasAiAgentService.updateAgent(pandasAiAgentService.listChatModelAgentId(resp.getId()));
        return resp;
    }

    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteModel(@PathVariable("id") Integer id) throws BaseException {
        chatModelService.deleteChatModel(id);
        pandasAiAgentService.deleteAgent(pandasAiAgentService.listChatModelAgentId(id));
        return true;
    }

    @RequestMapping("/getModelList")
    public List<ChatModel> getModelList() {
        return chatModelService.getChatModels();
    }

    @RequestMapping("/getModelAppList")
    public Map<String, ChatApp> getChatAppList() {
        return TrinoConstants.CHAT_INSTRUCTION_MAP;
//        return ChatAppManager.getAllApps(AppModule.CHAT);
    }

    @RequestMapping("/getModelParameters")
    public List<Parameter> getModelParameters() {
        return ChatModelParameters.getParameters();
    }

    @PostMapping("/testConnection")
    public boolean testConnection(@RequestBody ChatModelConfig modelConfig) {
        return ModelConfigHelper.testConnection(modelConfig);
    }
}
