package com.tencent.supersonic.sync_data.common.vo;

import lombok.Data;

import java.util.List;

/**
 * <b><code>AgentVO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/21 15:50
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Data
public class AgentVO {
    private Integer id;

    private String toolConfig;

    private String chatModelConfig;

    @Data
    public static class ToolConfig {
        private List<Tool> tools;
    }

    @Data
    public static class Tool {
        private List<Long> dataSetIds;

        private String type;
    }
}
