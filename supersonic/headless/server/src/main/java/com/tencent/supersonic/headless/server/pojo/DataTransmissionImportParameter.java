package com.tencent.supersonic.headless.server.pojo;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

/**
 * <b><code>DataTransmissionParameter</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/10 12:07
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Data
public class DataTransmissionImportParameter {

    @NotNull(message = "请选择数据域")
    private Long domainId;

    @NotNull(message = "请选择数据源")
    private Long databaseId;

    @NotNull(message = "请选择数据集")
    private MultipartFile data;
}
