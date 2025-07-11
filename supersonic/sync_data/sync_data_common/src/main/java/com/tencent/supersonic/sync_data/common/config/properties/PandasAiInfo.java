package com.tencent.supersonic.sync_data.common.config.properties;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * <b><code>PandasAiInfo</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/3 15:20
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */

@Data
@Component
@ConfigurationProperties(prefix = "pandas-ai")
public class PandasAiInfo {

    private String url;

}