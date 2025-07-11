package com.tencent.supersonic.sync_data.common.vo;

import lombok.Data;
import java.util.List;

/**
 * <b><code>ModelVO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 10:42
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
public class ModelVO {

    private Long id;

    private String name;

    private String bizName;

    private Long domainId;

    private Long databaseId;

    private String databaseName;

    private String description;

    private String modelDetail;

    // model_detail
//    private String queryType;
//
//    private String sqlQuery;
//
//    private String tableQuery;

    // model_detail.fields <fieldName, dataType>
//    private Map<String, String> fieldNameDataTypeMap;

    private List<DimensionVO> dimensionList;

    private List<MetricVO> metricList;

}
