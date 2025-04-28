package com.tencent.supersonic.headless.api.pojo.request;

import com.tencent.supersonic.common.pojo.enums.DataTypeEnums;
import com.tencent.supersonic.headless.api.pojo.DimValueMap;
import com.tencent.supersonic.headless.api.pojo.DimensionTimeTypeParams;
import com.tencent.supersonic.headless.api.pojo.SchemaItem;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Data
public class DimensionReq extends SchemaItem {

    private Long modelId;

    private String type;

    @NotNull(message = "expr can not be null")
    private String expr;

    // DATE ID CATEGORY
    private String semanticType = "CATEGORY";

    private String alias;

    private List<String> defaultValues;

    private List<DimValueMap> dimValueMaps;

    private DataTypeEnums dataType;

    private Map<String, Object> ext = new HashMap();

    private DimensionTimeTypeParams typeParams;
}
