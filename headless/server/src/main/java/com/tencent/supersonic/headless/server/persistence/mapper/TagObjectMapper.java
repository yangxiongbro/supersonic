package com.tencent.supersonic.headless.server.persistence.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.tencent.supersonic.headless.server.persistence.dataobject.TagObjectDO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface TagObjectMapper extends BaseMapper<TagObjectDO> {
}
