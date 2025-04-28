package com.tencent.supersonic.headless.api.pojo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Data;

import java.util.List;

@Data
public class ModelSchema {

    private String name;

    private String bizName;

    private String description;

    private List<ColumnSchema> columnSchemas;

    @JsonIgnore
    public ColumnSchema getColumnByName(String columnName) {
        for (ColumnSchema fieldSchema : columnSchemas) {
            if (fieldSchema.getColumnName().equalsIgnoreCase(columnName)) {
                return fieldSchema;
            }
        }
        return null;
    }

}
