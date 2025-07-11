package com.tencent.supersonic.headless.server.service;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.tencent.supersonic.common.pojo.ModelRela;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.server.persistence.dataobject.ModelRelaDO;

import java.util.List;

public interface ModelRelaService {

    void save(ModelRela modelRela, User user);

    void update(ModelRela modelRela, User user);

    List<ModelRela> getModelRelaList(Long domainId);

    List<ModelRela> getModelRela(List<Long> modelIds);

    ModelRela getModelRelaById(Long relaId);

    void delete(Long id);

    List<ModelRelaDO> listDo(Wrapper<ModelRelaDO> wrapper);

    Boolean batchSave(List<ModelRelaDO> list);
}
