package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.api.pojo.request.MetaBatchReq;
import com.tencent.supersonic.headless.api.pojo.request.TermReq;
import com.tencent.supersonic.headless.api.pojo.response.TermResp;
import com.tencent.supersonic.headless.server.service.TermService;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.cs.service.PandasAiAgentService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collections;
import java.util.List;

@RestController
@RequestMapping("/api/semantic/term")
public class TermController {

    @Autowired
    private TermService termService;
    @Autowired
    private PandasAiAgentService pandasAiAgentService;

    @PostMapping("/saveOrUpdate")
    @Transactional(rollbackFor = Exception.class)
    public boolean saveOrUpdate(@RequestBody TermReq termReq, HttpServletRequest request,
            HttpServletResponse response) throws BaseException {
        User user = UserHolder.findUser(request, response);
        termService.saveOrUpdate(termReq, user);
        List<Long> termIdList;
        if(null == termReq.getId()) {
            termIdList = termService.getTerms(termReq.getDomainId(), termReq.getName()).stream().map(TermResp::getId).toList();
        } else {
            termIdList = Collections.singletonList(termReq.getId());
        }
        pandasAiAgentService.updateAgent(pandasAiAgentService.getAgentIdList(pandasAiAgentService.listDataSetIdByTermId(termIdList)));
        return true;
    }

    @GetMapping
    public List<TermResp> getTerms(@RequestParam("domainId") Long domainId,
            @RequestParam(name = "queryKey", required = false) String queryKey) {
        return termService.getTerms(domainId, queryKey);
    }

    @Deprecated
    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public boolean delete(@PathVariable("id") Long id) throws BaseException {
        termService.delete(id);
        pandasAiAgentService.deleteAgent(pandasAiAgentService.getAgentIdList(pandasAiAgentService.listDataSetIdByTermId(Collections.singletonList(id))));
        return true;
    }

    @PostMapping("/deleteBatch")
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteBatch(@RequestBody MetaBatchReq metaBatchReq) throws BaseException {
        List<Long> dataSetIdList = pandasAiAgentService.listDataSetIdByTermId(metaBatchReq.getIds());
        termService.deleteBatch(metaBatchReq);
        pandasAiAgentService.deleteAgent(pandasAiAgentService.getAgentIdList(dataSetIdList));
        return true;
    }
}
