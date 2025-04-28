package com.tencent.supersonic.headless.api.pojo.request;

import lombok.Data;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Data
public class QueryFilters implements Serializable {
    private List<QueryFilter> filters = new ArrayList<>();
    private Map<String, Object> params = new HashMap<>();
}
