package com.tencent.supersonic.headless.api.pojo.response;

import com.tencent.supersonic.common.pojo.enums.DataTypeEnums;
import com.tencent.supersonic.headless.api.pojo.DimValueMap;
import com.tencent.supersonic.headless.api.pojo.DimensionTimeTypeParams;
import com.tencent.supersonic.headless.api.pojo.SchemaItem;
import com.tencent.supersonic.headless.api.pojo.enums.DimensionType;
import lombok.Data;
import lombok.ToString;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Data
@ToString(callSuper = true)
public class DimensionResp extends SchemaItem {

    private Long modelId;

    private Long domainId;

    private DimensionType type;

    private String expr;

    private String modelName;

    private String modelBizName;

    private String modelFilterSql;
    // DATE ID CATEGORY
    private String semanticType;

    private String alias;

    private List<String> defaultValues;

    private List<DimValueMap> dimValueMaps;

    private DataTypeEnums dataType;

    private int isTag;

    private DimensionTimeTypeParams typeParams;

    private Map<String, Object> ext = new HashMap<>();

    public boolean isTimeDimension() {
        return DimensionType.isTimeDimension(type);
    }

    public boolean isPartitionTime() {
        return DimensionType.isPartitionTime(type);
    }
}
