package com.tencent.supersonic.sync_data.common.vo;

import com.tencent.supersonic.headless.api.pojo.enums.MetricDefineType;
import lombok.Data;

/**
 * <b><code>MetricVO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 11:20
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
public class MetricVO {
    private Long modelId;

    private String name;

    private String bizName;

    private String typeParams;

    // type_params.expr
//    private String expr;

    private MetricDefineType defineType;

    private String description;

}
