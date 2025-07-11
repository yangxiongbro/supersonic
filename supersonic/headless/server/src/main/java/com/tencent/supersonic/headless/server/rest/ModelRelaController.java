package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.common.pojo.ModelRela;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.server.service.ModelRelaService;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.cs.service.PandasAiSchemaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Stream;

@RestController
@RequestMapping("/api/semantic/modelRela")
public class ModelRelaController {

    @Autowired
    private ModelRelaService modelRelaService;

    @Autowired
    private PandasAiSchemaService pandasAiSchemaService;

    @PostMapping
    @Transactional(rollbackFor = Exception.class)
    public boolean save(@RequestBody ModelRela modelRela, User user) throws BaseException {
        modelRelaService.save(modelRela, user);
        pandasAiSchemaService.updateSchema(Stream.of(modelRela.getFromModelId(), modelRela.getToModelId()).toList());
        return true;
    }

    @PutMapping
    @Transactional(rollbackFor = Exception.class)
    public boolean update(@RequestBody ModelRela modelRela, User user) throws BaseException {
        modelRelaService.update(modelRela, user);
        pandasAiSchemaService.updateSchema(Stream.of(modelRela.getFromModelId(), modelRela.getToModelId()).toList());
        return true;
    }

    @RequestMapping("/list")
    public List<ModelRela> getModelRelaList(@RequestParam("domainId") Long domainId) {
        return modelRelaService.getModelRelaList(domainId);
    }

    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public void delete(@PathVariable("id") Long id) throws BaseException {
        ModelRela modelRela = modelRelaService.getModelRelaById(id);
        modelRelaService.delete(id);
        pandasAiSchemaService.updateSchema(Stream.of(modelRela.getFromModelId(), modelRela.getToModelId()).toList());
    }
}
