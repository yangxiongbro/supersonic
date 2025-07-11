package com.tencent.supersonic.sync_data.cs.mapper;

import com.tencent.supersonic.sync_data.common.vo.AgentVO;
import org.apache.ibatis.annotations.Mapper;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * <b><code>PandasAiAgentMapper</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/21 15:19
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Repository
@Mapper
public interface PandasAiAgentMapper {

    List<Long> listDataSetIdByTermId(List<Long> termIdList);

    List<AgentVO> listDateSetAgent();

    List<Integer> listChatModelAgentId(Integer chatModelId);
}
