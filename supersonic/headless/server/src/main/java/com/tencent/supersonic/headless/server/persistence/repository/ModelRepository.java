package com.tencent.supersonic.headless.server.persistence.repository;

import com.tencent.supersonic.headless.server.persistence.dataobject.ModelDO;
import com.tencent.supersonic.headless.server.pojo.ModelFilter;

import java.util.Collection;
import java.util.List;

public interface ModelRepository {

    void createModel(ModelDO modelDO);

    void batchCreate(Collection<ModelDO> datasourceDOList);

    void updateModel(ModelDO modelDO);

    List<ModelDO> getModelList(ModelFilter modelFilter);

    ModelDO getModelById(Long id);

    void batchUpdate(List<ModelDO> modelDOS);
}
