package com.tencent.supersonic.headless.server.dto;

import com.tencent.supersonic.headless.server.persistence.dataobject.MetricDO;
import lombok.Data;

/**
 * <b><code>MetricDTO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/4 14:16
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Data
public class MetricDTO extends MetricDO {
    private Long originId;
}
