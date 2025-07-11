package com.tencent.supersonic.sync_data.common.vo;

import lombok.Data;

/**
 * <b><code>DimensionVO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 11:19
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
public class DimensionVO {
    private Long modelId;

    private String name;

    private String expr;

    private String bizName;

    private String description;
}
