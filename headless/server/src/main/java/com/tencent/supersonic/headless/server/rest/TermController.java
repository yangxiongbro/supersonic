package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.api.pojo.request.MetaBatchReq;
import com.tencent.supersonic.headless.api.pojo.request.TermReq;
import com.tencent.supersonic.headless.api.pojo.response.TermResp;
import com.tencent.supersonic.headless.server.service.TermService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/semantic/term")
public class TermController {

    @Autowired
    private TermService termService;

    @PostMapping("/saveOrUpdate")
    public boolean saveOrUpdate(@RequestBody TermReq termReq, HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        termService.saveOrUpdate(termReq, user);
        return true;
    }

    @GetMapping
    public List<TermResp> getTerms(@RequestParam("domainId") Long domainId,
            @RequestParam(name = "queryKey", required = false) String queryKey) {
        return termService.getTerms(domainId, queryKey);
    }

    @Deprecated
    @DeleteMapping("/{id}")
    public boolean delete(@PathVariable("id") Long id) {
        termService.delete(id);
        return true;
    }

    @PostMapping("/deleteBatch")
    public boolean deleteBatch(@RequestBody MetaBatchReq metaBatchReq) {
        termService.deleteBatch(metaBatchReq);
        return true;
    }
}
