package com.tencent.supersonic.headless.server.service;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.api.pojo.request.MetaBatchReq;
import com.tencent.supersonic.headless.api.pojo.request.TermReq;
import com.tencent.supersonic.headless.api.pojo.response.TermResp;
import com.tencent.supersonic.headless.server.persistence.dataobject.TermDO;

import java.util.List;
import java.util.Map;
import java.util.Set;

public interface TermService {

    void saveOrUpdate(TermReq termSetReq, User user);

    void delete(Long id);

    void deleteBatch(MetaBatchReq metaBatchReq);

    List<TermResp> getTerms(Long domainId, String queryKey);

    Map<Long, List<TermResp>> getTermSets(Set<Long> domainIds);

    List<TermDO> listDo(Wrapper<TermDO> wrapper);

    Boolean batchSave(List<TermDO> list);
}
