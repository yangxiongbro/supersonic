package com.tencent.supersonic.headless.server.rest;

import com.google.common.collect.Lists;
import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.common.pojo.enums.AuthType;
import com.tencent.supersonic.headless.api.pojo.ModelSchema;
import com.tencent.supersonic.headless.api.pojo.request.FieldRemovedReq;
import com.tencent.supersonic.headless.api.pojo.request.MetaBatchReq;
import com.tencent.supersonic.headless.api.pojo.request.ModelBuildReq;
import com.tencent.supersonic.headless.api.pojo.request.ModelReq;
import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;
import com.tencent.supersonic.headless.api.pojo.response.ModelResp;
import com.tencent.supersonic.headless.api.pojo.response.UnAvailableItemResp;
import com.tencent.supersonic.headless.server.pojo.ModelFilter;
import com.tencent.supersonic.headless.server.service.ModelService;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.cs.service.PandasAiSchemaService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.sql.SQLException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/semantic/model")
public class ModelController {

    private ModelService modelService;

    private PandasAiSchemaService pandasAiSchemaService;

    public ModelController(ModelService modelService, PandasAiSchemaService pandasAiSchemaService) {
        this.modelService = modelService;
        this.pandasAiSchemaService = pandasAiSchemaService;
    }

    @PostMapping("/createModel")
    @Transactional(rollbackFor = Exception.class)
    public Boolean createModel(@RequestBody ModelReq modelReq, HttpServletRequest request,
            HttpServletResponse response) throws Exception {
        User user = UserHolder.findUser(request, response);
        ModelResp resp = modelService.createModel(modelReq, user);
        pandasAiSchemaService.createSchema(Collections.singletonList(resp));
        return true;
    }

    @PostMapping("/createModelBatch")
    @Transactional(rollbackFor = Exception.class)
    public Boolean createModelBatch(@RequestBody ModelBuildReq modelBuildReq,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        User user = UserHolder.findUser(request, response);
        List<ModelResp> respList = modelService.createModel(modelBuildReq, user);
        pandasAiSchemaService.createSchema(respList);
        return true;
    }

    @PostMapping("/updateModel")
    @Transactional(rollbackFor = Exception.class)
    public Boolean updateModel(@RequestBody ModelReq modelReq, HttpServletRequest request,
            HttpServletResponse response) throws Exception {
        User user = UserHolder.findUser(request, response);
        modelService.updateModel(modelReq, user);
        pandasAiSchemaService.updateSchema(Collections.singletonList(modelReq.getId()));
        return true;
    }

    @DeleteMapping("/deleteModel/{modelId}")
    @Transactional(rollbackFor = Exception.class)
    public Boolean deleteModel(@PathVariable("modelId") Long modelId, HttpServletRequest request,
            HttpServletResponse response) throws BaseException {
        User user = UserHolder.findUser(request, response);
        modelService.deleteModel(modelId, user);
        pandasAiSchemaService.deleteSchema(Collections.singletonList(modelId));
        return true;
    }

    @GetMapping("/getModelList/{domainId}")
    public List<ModelResp> getModelList(@PathVariable("domainId") Long domainId,
            HttpServletRequest request, HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return modelService.getModelListWithAuth(user, domainId, AuthType.ADMIN);
    }

    @GetMapping("/getModel/{id}")
    public ModelResp getModel(@PathVariable("id") Long id) {
        return modelService.getModel(id);
    }

    @GetMapping("/getModelListByIds/{modelIds}")
    public List<ModelResp> getModelListByIds(@PathVariable("modelIds") String modelIds) {
        List<Long> ids = Arrays.stream(modelIds.split(",")).map(Long::parseLong)
                .collect(Collectors.toList());
        ModelFilter modelFilter = new ModelFilter();
        modelFilter.setIds(ids);
        return modelService.getModelList(modelFilter);
    }

    @GetMapping("/getAllModelByDomainId")
    public List<ModelResp> getAllModelByDomainId(@RequestParam("domainId") Long domainId) {
        return modelService.getAllModelByDomainIds(Lists.newArrayList(domainId));
    }

    @GetMapping("/getModelDatabase/{modelId}")
    public DatabaseResp getModelDatabase(@PathVariable("modelId") Long modelId) {
        return modelService.getDatabaseByModelId(modelId);
    }

    @PostMapping("/batchUpdateStatus")
    public Boolean batchUpdateStatus(@RequestBody MetaBatchReq metaBatchReq,
            HttpServletRequest request, HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        modelService.batchUpdateStatus(metaBatchReq, user);
        return true;
    }

    @PostMapping("/getUnAvailableItem")
    public UnAvailableItemResp getUnAvailableItem(@RequestBody FieldRemovedReq fieldRemovedReq) {
        return modelService.getUnAvailableItem(fieldRemovedReq);
    }

    @PostMapping("/buildModelSchema")
    public Map<String, ModelSchema> buildModelSchema(@RequestBody ModelBuildReq modelBuildReq)
            throws SQLException {
        return modelService.buildModelSchema(modelBuildReq);
    }
}
