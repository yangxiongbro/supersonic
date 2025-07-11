package com.tencent.supersonic.sync_data.common.vo;

import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * <b><code>PandasAiChatResponse</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/5 17:05
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
public class PandasAiChatResponse {
    private String sql;
    private String sql_explain;
    private List<Map<String, Object>> data;
    private String question;
    private String title;
    private String explanatory;
    private PandasAiChatResponse.TableVisualizationConfig table_visualization_config;
    private List<AnalysisInfo> analysis_info;
    @Data
    public static class TableVisualizationConfig {
        private Boolean show_index;
        private List<Map<String, String>> columns;
    }
    @Data
    public static class AnalysisInfo {
        private List<String> dimensions;
        private String metric;
        private String user_chart_type;
        private String recommend_chart_type;
        private String recommend_reason;
        private List<Object> data_item_mark_point;
    }
}