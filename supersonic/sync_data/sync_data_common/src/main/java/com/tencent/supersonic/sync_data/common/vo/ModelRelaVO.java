package com.tencent.supersonic.sync_data.common.vo;

import lombok.Data;

/**
 * <b><code>ModelRelaVO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 17:11
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
public class ModelRelaVO {
    private Long modelId;

    private String joinBizName;

    private String joinModelDetail;

    private String joinCondition;

    private Boolean isFrom;
}
