package com.tencent.supersonic.chat.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.chat.server.agent.Agent;
import com.tencent.supersonic.chat.server.agent.AgentToolType;
import com.tencent.supersonic.chat.server.service.AgentService;
import com.tencent.supersonic.common.pojo.ChatApp;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.common.pojo.enums.AuthType;
import com.tencent.supersonic.common.util.JsonUtil;
import com.tencent.supersonic.headless.chat.corrector.LLMSqlCorrector;
import com.tencent.supersonic.headless.chat.parser.llm.OnePassSCSqlGenStrategy;
import com.tencent.supersonic.sync_data.common.constants.TrinoConstants;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.cs.service.PandasAiAgentService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collections;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping({"/api/chat/agent", "/openapi/chat/agent"})
public class AgentController {

    @Autowired
    private AgentService agentService;

    @Autowired
    private PandasAiAgentService pandasAiAgentService;

    @PostMapping
    public Agent createAgent(@RequestBody Agent agent, HttpServletRequest httpServletRequest,
            HttpServletResponse httpServletResponse) {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        setDefaultPrompt(agent);
        return agentService.createAgent(agent, user);
    }

    @PutMapping
    @Transactional(rollbackFor = Exception.class)
    public Agent updateAgent(@RequestBody Agent agent, HttpServletRequest httpServletRequest,
            HttpServletResponse httpServletResponse) throws BaseException {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        Agent resp = agentService.updateAgent(agent, user);
        pandasAiAgentService.updateAgent(Collections.singletonList(resp.getId()));
        return resp;
    }

    @PostMapping("/byOther")
    public Agent createAgentByOther(@RequestBody Agent agent, HttpServletRequest httpServletRequest,
                             HttpServletResponse httpServletResponse) {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        setDefaultPrompt(agent);
        return agentService.createAgent(agent, user);
    }

    @PutMapping("/byOther")
    @Transactional(rollbackFor = Exception.class)
    public Agent updateAgentByOther(@RequestBody Agent agent, HttpServletRequest httpServletRequest,
                             HttpServletResponse httpServletResponse) throws BaseException {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        setOriginPrompt(agent);
        Agent resp = agentService.updateAgent(agent, user);
        pandasAiAgentService.updateAgent(Collections.singletonList(resp.getId()));
        return resp;
    }

    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteAgent(@PathVariable("id") Integer id) throws BaseException {
        agentService.deleteAgent(id);
        pandasAiAgentService.deleteAgent(Collections.singletonList(id));
        return true;
    }

    @RequestMapping("/getAgentList")
    public List<Agent> getAgentList(
            @RequestParam(value = "authType", required = false) AuthType authType,
            HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) {
        User user = UserHolder.findUser(httpServletRequest, httpServletResponse);
        return agentService.getAgents(user, authType);
    }

    @RequestMapping("/getToolTypes")
    public Map<AgentToolType, String> getToolTypes() {
        return AgentToolType.getToolTypes();
    }


    private void setDefaultPrompt(Agent agent){
        if (CollectionUtils.isEmpty(agent.getChatAppConfig())){
            return;
        }
        ChatApp chatApp = agent.getChatAppConfig().get("S2SQL_PARSER");
        if(null != chatApp && chatApp.isEnable() && !StringUtils.hasText(chatApp.getPrompt())){
            chatApp.setPrompt(TrinoConstants.CHAT_INSTRUCTION_MAP.get(OnePassSCSqlGenStrategy.APP_KEY).getPrompt());
        }
        chatApp = agent.getChatAppConfig().get("S2SQL_CORRECTOR");
        if(null != chatApp && chatApp.isEnable() && !StringUtils.hasText(chatApp.getPrompt())){
            chatApp.setPrompt(TrinoConstants.CHAT_INSTRUCTION_MAP.get(LLMSqlCorrector.APP_KEY).getPrompt());
        }
    }

    private void setOriginPrompt(Agent agent){
        Map<String, ChatApp> newChatAppConfig = agent.getChatAppConfig();
        if (CollectionUtils.isEmpty(newChatAppConfig)){
            return;
        }
        Map<String, ChatApp> originChatAppConfig = agentService.getAgent(agent.getId()).getChatAppConfig();
        if (CollectionUtils.isEmpty(originChatAppConfig)){
            return;
        }
        ChatApp originChatApp = originChatAppConfig.get("S2SQL_PARSER");
        ChatApp newChatApp = newChatAppConfig.get("S2SQL_PARSER");
        if(null != originChatApp && null != newChatApp){
            newChatApp.setPrompt(originChatApp.getPrompt());
        }
        originChatApp = originChatAppConfig.get("S2SQL_CORRECTOR");
        newChatApp = newChatAppConfig.get("S2SQL_CORRECTOR");
        if(null != originChatApp && null != newChatApp){
            newChatApp.setPrompt(originChatApp.getPrompt());
        }
    }
}
