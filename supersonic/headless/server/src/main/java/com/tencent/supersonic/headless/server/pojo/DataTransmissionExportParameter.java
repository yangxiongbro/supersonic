package com.tencent.supersonic.headless.server.pojo;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

/**
 * <b><code>DataTransmissionExportParameter</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/10 14:25
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Data
public class DataTransmissionExportParameter {

    @NotNull(message = "请选择数据域")
    private Long domainId;

    private List<Long> dataSetIdList;
}
