package com.tencent.supersonic.sync_data.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * <b><code>SchemaDTO</code></b>
 * <p/>
 * 创建pandas-ai schema信息dto
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 14:27
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SchemaDTO {
    @JsonProperty("table_name")
    private String tableName;

    @JsonProperty("domain_id")
    private Long domainId;

    @JsonProperty("database_id")
    private Long databaseId;

    @JsonProperty("database_name")
    private String databaseName;

    @JsonProperty("catalog_name")
    private String catalogName;

    private String description;

    private SourceDTO source;

    private List<ColumnDTO> columns;

    private List<RelationDTO> relations;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class SourceDTO{
        private String type;

        private ConnectionDTO connection;

        @JsonInclude(JsonInclude.Include.NON_NULL)
        private String table;

        @JsonInclude(JsonInclude.Include.NON_NULL)
        private String view;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ConnectionDTO{

        private String host;

        private String port;

        private String user;

        private String password;

        private String database;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ColumnDTO{
        private String name;

        private String alias;

        private String type;

        @JsonInclude(JsonInclude.Include.NON_NULL)
        private String expression;

        private String description;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class RelationDTO{
        private String name;

        private String description;

        private String from;

        private String to;
    }
}
