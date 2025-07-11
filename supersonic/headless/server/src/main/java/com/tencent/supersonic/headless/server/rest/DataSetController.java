package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.api.pojo.MetaFilter;
import com.tencent.supersonic.headless.api.pojo.request.DataSetReq;
import com.tencent.supersonic.headless.api.pojo.response.DataSetResp;
import com.tencent.supersonic.headless.server.service.DataSetService;
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
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collections;
import java.util.List;

@RestController
@RequestMapping("/api/semantic/dataSet")
public class DataSetController {

    @Autowired
    private DataSetService dataSetService;
    @Autowired
    private PandasAiAgentService pandasAiAgentService;

    @PostMapping
    public DataSetResp save(@RequestBody DataSetReq dataSetReq, HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return dataSetService.save(dataSetReq, user);
    }

    @PutMapping
    @Transactional(rollbackFor = Exception.class)
    public DataSetResp update(@RequestBody DataSetReq dataSetReq, HttpServletRequest request,
            HttpServletResponse response) throws BaseException {
        User user = UserHolder.findUser(request, response);
        DataSetResp resp = dataSetService.update(dataSetReq, user);
        pandasAiAgentService.updateAgent(pandasAiAgentService.getAgentIdList(Collections.singletonList(resp.getId())));
        return resp;
    }

    @GetMapping("/{id}")
    public DataSetResp getDataSet(@PathVariable("id") Long id) {
        return dataSetService.getDataSet(id);
    }

    @GetMapping("/getDataSetList")
    public List<DataSetResp> getDataSetList(@RequestParam("domainId") Long domainId) {
        MetaFilter metaFilter = new MetaFilter();
        metaFilter.setDomainId(domainId);
        return dataSetService.getDataSetList(metaFilter);
    }

    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public Boolean delete(@PathVariable("id") Long id, HttpServletRequest request,
            HttpServletResponse response) throws BaseException {
        User user = UserHolder.findUser(request, response);
        dataSetService.delete(id, user);
        pandasAiAgentService.deleteAgent(pandasAiAgentService.getAgentIdList(Collections.singletonList(id)));
        return true;
    }
}
