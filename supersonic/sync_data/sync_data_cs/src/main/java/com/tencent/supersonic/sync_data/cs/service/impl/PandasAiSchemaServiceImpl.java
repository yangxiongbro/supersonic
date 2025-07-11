package com.tencent.supersonic.sync_data.cs.service.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.tencent.supersonic.common.util.JsonUtil;
import com.tencent.supersonic.headless.api.pojo.SchemaItem;
import com.tencent.supersonic.headless.api.pojo.enums.MetricDefineType;
import com.tencent.supersonic.headless.api.pojo.response.ModelResp;
import com.tencent.supersonic.headless.core.pojo.ConnectInfo;
import com.tencent.supersonic.sync_data.common.config.properties.PandasAiInfo;
import com.tencent.supersonic.sync_data.common.constants.TrinoConstants;
import com.tencent.supersonic.sync_data.common.dto.SchemaDTO;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.exception.business.BusinessExceptionAssertResponseEnum;
import com.tencent.supersonic.sync_data.common.utils.TrinoUtils;
import com.tencent.supersonic.sync_data.common.utils.UrlUtils;
import com.tencent.supersonic.sync_data.common.vo.*;
import com.tencent.supersonic.sync_data.cs.mapper.PandasAiSchemaMapper;
import com.tencent.supersonic.sync_data.cs.service.PandasAiSchemaService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.stream.Collectors;

/**
 * <b><code>PandasAiSchemaServiceImpl</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 11:38
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Slf4j
@Service
public class PandasAiSchemaServiceImpl implements PandasAiSchemaService {

    private ConnectInfo trinoConnectInfo;

    private PandasAiInfo pandasAiInfo;

    private PandasAiSchemaMapper pandasAiSchemaMapper;

    private RestTemplate restTemplateWithLogging;

    public PandasAiSchemaServiceImpl(ConnectInfo trinoConnectInfo, PandasAiInfo pandasAiInfo, PandasAiSchemaMapper pandasAiSchemaMapper, RestTemplate restTemplateWithLogging){
        this.trinoConnectInfo = trinoConnectInfo;
        this.pandasAiInfo = pandasAiInfo;
        this.pandasAiSchemaMapper = pandasAiSchemaMapper;
        this.restTemplateWithLogging = restTemplateWithLogging;
    }

    public Integer createSchema(List<ModelResp> modelRespList) throws BaseException {
        return createSchemaByModelId(modelRespList.stream().map(SchemaItem::getId).toList());
    }

    public Integer createSchemaByModelId(List<Long> modelIdList) throws BaseException {
        if (CollectionUtils.isEmpty(modelIdList)) {
            return 0;
        }
        List<SchemaDTO> schemaDTOList = getSchemaInfos(modelIdList);

        ResponseEntity<PandasAiResponse<Integer>> responseEntity = restTemplateWithLogging.exchange(
                pandasAiInfo.getUrl()+"/sync_data/create_schema",
                HttpMethod.POST,
                new HttpEntity<>(Collections.singletonMap("schemaInfos", schemaDTOList), TrinoConstants.POST_HEADERS),
                new ParameterizedTypeReference<>() {});
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertNotNull(responseEntity.getBody(), "空的响应");
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertTrue(200 == responseEntity.getBody().getCode(), responseEntity.getBody().getMsg());
        return responseEntity.getBody().getData();
    }

    public Integer deleteSchema(List<Long> modelIdList) throws BaseException {
        if(CollectionUtils.isEmpty(modelIdList)){
            return 0;
        }
        ResponseEntity<PandasAiResponse<Integer>> responseEntity = restTemplateWithLogging.exchange(
                pandasAiInfo.getUrl()+"/sync_data/delete_schema",
                HttpMethod.POST,
                new HttpEntity<>(Collections.singletonMap("modelIdList", modelIdList), TrinoConstants.POST_HEADERS),
                new ParameterizedTypeReference<>() {});
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertNotNull(responseEntity.getBody(), "空的响应");
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertTrue(200 == responseEntity.getBody().getCode(), responseEntity.getBody().getMsg());
        return responseEntity.getBody().getData();
    }

    public Integer updateSchema(List<Long> modelIdList) throws BaseException {
        List<SchemaDTO> schemaDTOList = getSchemaInfos(modelIdList);

        ResponseEntity<PandasAiResponse<Integer>> responseEntity = restTemplateWithLogging.exchange(
                pandasAiInfo.getUrl()+"/sync_data/update_schema",
                HttpMethod.POST,
                new HttpEntity<>(Collections.singletonMap("schemaInfos", schemaDTOList), TrinoConstants.POST_HEADERS),
                new ParameterizedTypeReference<>() {});
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertNotNull(responseEntity.getBody(), "空的响应");
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertTrue(200 == responseEntity.getBody().getCode(), responseEntity.getBody().getMsg());
        return responseEntity.getBody().getData();
    }

    public List<SchemaDTO> getSchemaInfos(List<Long> modelIdList){
        List<ModelVO> modelVOList = pandasAiSchemaMapper.listModel(modelIdList);
        Map<Long, List<DimensionVO>> dimensionVOListMap = pandasAiSchemaMapper.listDimension(modelIdList).stream().collect(Collectors.groupingBy(DimensionVO::getModelId));
        Map<Long, List<MetricVO>> metricVOListMap = pandasAiSchemaMapper.listMetric(modelIdList).stream().collect(Collectors.groupingBy(MetricVO::getModelId));
        Map<Long, List<ModelRelaVO>> modelRelaVOListMap = pandasAiSchemaMapper.listModelRela(modelIdList).stream().collect(Collectors.groupingBy(ModelRelaVO::getModelId));
        List<SchemaDTO> schemaDTOList = new ArrayList<>(modelVOList.size());
        for(ModelVO modelVO : modelVOList){
            SchemaDTO schemaDTO = convertSchema(
                    modelVO,
                    Optional.ofNullable(dimensionVOListMap.get(modelVO.getId())).orElse(Collections.emptyList()),
                    Optional.ofNullable(metricVOListMap.get(modelVO.getId())).orElse(Collections.emptyList()),
                    Optional.ofNullable(modelRelaVOListMap.get(modelVO.getId())).orElse(Collections.emptyList())
            );
//            System.out.println(schemaDTO);
            schemaDTOList.add(schemaDTO);
        }
        return schemaDTOList;
    }

    private SchemaDTO convertSchema(ModelVO model, List<DimensionVO> dimensionList, List<MetricVO> metricList, List<ModelRelaVO> modelRelaList){
        log.info("convertSchema：{}", model);
        String catalogName = TrinoUtils.getCatalogName(model.getDatabaseId());
        Map<String, Object> modelDetailMap = StringUtils.hasText(model.getModelDetail()) ? JsonUtil.toMap(model.getModelDetail(), String.class, Object.class) : Collections.emptyMap();
        String tableName = getTableName(modelDetailMap, model.getBizName());

        String[] ipHost = UrlUtils.extractIpPort(trinoConnectInfo.getUrl());
        // source
        SchemaDTO.SourceDTO source = new SchemaDTO.SourceDTO(
                "trino",
                new SchemaDTO.ConnectionDTO(
                        ipHost[0],
                        ipHost[1],
                        trinoConnectInfo.getUserName(),
                        trinoConnectInfo.getPassword(),
                        catalogName),
                TrinoUtils.doubleQuoteEachIdentifiers(tableName),
                getView(modelDetailMap));

        // columns
        Map<String, String> fieldNameDataTypeMap = null == modelDetailMap.get("fields") ? Collections.emptyMap() :
                ((List<Map<String, Object>>) modelDetailMap.get("fields")).stream().collect(Collectors.toMap(
                        item -> Optional.ofNullable((String) item.get("fieldName")).orElse("").toLowerCase(),
                        item -> (String)Optional.ofNullable(item.get("dataType")).orElse(""),
                        (key1, key2) -> key2));

        List<SchemaDTO.ColumnDTO> columns = new ArrayList<>();
        Set<String> uniqueColumns = new HashSet<>(dimensionList.size() + metricList.size());
        addDimensionColumn(dimensionList, fieldNameDataTypeMap, uniqueColumns, columns);
        addMetricColumn(metricList, fieldNameDataTypeMap, uniqueColumns, columns);
        List<SchemaDTO.RelationDTO> relations = getRelations(modelRelaList);
        String description = StringUtils.hasText(model.getDescription()) ? model.getDescription() : model.getName();
        return new SchemaDTO(tableName, model.getDomainId(), model.getDatabaseId(), model.getDatabaseName(), catalogName, description, source, columns, relations);
    }

    private void addDimensionColumn(List<DimensionVO> dimensionList, Map<String, String> fieldNameDataTypeMap, Set<String> uniqueColumns, List<SchemaDTO.ColumnDTO> columns){
        if(CollectionUtils.isEmpty(dimensionList)){
            return;
        }
        for(DimensionVO dimensionVO : dimensionList){
            SchemaDTO.ColumnDTO columnDTO = new SchemaDTO.ColumnDTO();
            columnDTO.setName(dimensionVO.getBizName());
            columnDTO.setAlias(dimensionVO.getName());
            columnDTO.setDescription(dimensionVO.getDescription());
            if(null != dimensionVO.getBizName() && dimensionVO.getBizName().equals(dimensionVO.getExpr())){
                columnDTO.setType(typeMapping(fieldNameDataTypeMap.get(dimensionVO.getBizName().toLowerCase())));
            } else {
                columnDTO.setType("float");
                columnDTO.setExpression(dimensionVO.getExpr());
            }
            if(uniqueColumns.contains(columnDTO.getName())){
                continue;
            } else {
                uniqueColumns.add(columnDTO.getName());
            }
            columns.add(columnDTO);
        }
    }

    /**
     * @description:
     * 1、如果define_type字段值是METRIC,那么type_params 的exp是一个表达式，例如： {"expr":"pv/uv","metrics":[{"bizName":"pv","id":3},{"bizName":"uv","id":2}]}
     * 2、如果如果define_type字段值是FIELD，那么type_params的expr就是一个表达式，例如： {"expr":"count(distinct user_name)","fields":[{"fieldName":"user_name"}]}
     * 3、如果如果define_type字段值是MEASURE，那么type_params的expr就是数据库原字段名
     * 所以3种情况都是返回exp的值作为字段名，但1、2要加多个标记表示是表达式计算的
     *
     * @param: metricList
     * @param: fieldNameDataTypeMap
     * @param: columns
     * @return:
     * @throws
     * @author yang xiong
     * @date 2025/6/16 15:05
     **/
    private void addMetricColumn(List<MetricVO> metricList, Map<String, String> fieldNameDataTypeMap, Set<String> uniqueColumns, List<SchemaDTO.ColumnDTO> columns){
        if(CollectionUtils.isEmpty(metricList)){
            return;
        }
        for(MetricVO metricVO : metricList){
            Map<String, Object> typeParamsMap = JsonUtil.toMap(Optional.ofNullable(metricVO.getTypeParams()).orElse("{}"), String.class, Object.class);
            String expr = (String)typeParamsMap.get("expr");
            if(!StringUtils.hasText(expr)){
                continue;
            }
            SchemaDTO.ColumnDTO columnDTO = new SchemaDTO.ColumnDTO();
            columnDTO.setAlias(metricVO.getName());
            columnDTO.setDescription(metricVO.getDescription());
            if(MetricDefineType.METRIC.equals(metricVO.getDefineType()) || MetricDefineType.FIELD.equals(metricVO.getDefineType())){
                columnDTO.setName(metricVO.getBizName());
                columnDTO.setExpression(expr);
                columnDTO.setType("float");
            } else if(MetricDefineType.MEASURE.equals(metricVO.getDefineType())){
                columnDTO.setName(expr);
                columnDTO.setType(typeMapping(fieldNameDataTypeMap.get(expr.toLowerCase())));
            } else {
                continue;
            }
            if(uniqueColumns.contains(columnDTO.getName())){
                continue;
            } else {
                uniqueColumns.add(columnDTO.getName());
            }
            columns.add(columnDTO);
        }
    }

    /**
     * @description: 模型关联关系
     * @param: modelRelaList
     * @return: java.util.List<com.tencent.supersonic.sync_data.common.dto.SchemaDTO.RelationDTO>
     * @throws
     * @author yang xiong
     * @date 2025/6/28 01:53
     **/
    private List<SchemaDTO.RelationDTO> getRelations(List<ModelRelaVO> modelRelaList){
        if(CollectionUtils.isEmpty(modelRelaList)){
            return Collections.emptyList();
        }
        List<SchemaDTO.RelationDTO> relations = new ArrayList<>();
        for(ModelRelaVO modelRelaVO:modelRelaList){
            String joinTableName = TrinoUtils.doubleQuoteEachIdentifiers(
                    getTableName(
                            StringUtils.hasText(modelRelaVO.getJoinModelDetail()) ? JsonUtil.toMap(modelRelaVO.getJoinModelDetail(), String.class, Object.class) : Collections.emptyMap(),
                            modelRelaVO.getJoinBizName()));
            List<Map<String, Object>> joinConditionMapList = JsonUtil.toObject(Optional.ofNullable(modelRelaVO.getJoinCondition()).orElse("[]"), new TypeReference<>() {});
            for(Map<String, Object> joinConditionMap : joinConditionMapList){
//                String to = (String)joinConditionMap.get(Boolean.TRUE.equals(modelRelaVO.getIsFrom()) ? "leftField" : "rightField");
//                relationMap.computeIfAbsent(to,
//                key -> new SchemaDTO.RelationDTO(null, null, new ArrayList<>(), to)).getFrom().add(
//                        String.format("%s.%s", joinTableName, joinConditionMap.get(Boolean.TRUE.equals(modelRelaVO.getIsFrom()) ? "rightField" : "leftField"))
//                );
                relations.add(
                        new SchemaDTO.RelationDTO(null, null,
                                String.format("%s.%s", joinTableName, joinConditionMap.get(Boolean.TRUE.equals(modelRelaVO.getIsFrom()) ? "rightField" : "leftField")),
                                (String)joinConditionMap.get(Boolean.TRUE.equals(modelRelaVO.getIsFrom()) ? "leftField" : "rightField")
                        ));
            }
        }
        return relations;
    }

    /**
     * @description: 数据库字段类型映射
     * @param: originType
     * @return: java.lang.String
     * @throws
     * @author yang xiong
     * @date 2025/6/28 01:53
     **/
    private String typeMapping(String originType){
        if(StringUtils.hasText(originType)){
            String originTypeLower = originType.toLowerCase();
            if(originTypeLower.contains("int")){
                return "integer";
            } else if (originTypeLower.contains("date") || originTypeLower.contains("time")){
                return "datetime";
            } else if (originTypeLower.contains("char") || originTypeLower.contains("text") || originTypeLower.contains("lob") || originTypeLower.contains("json") || originTypeLower.contains("xml")){
                return "string";
            } else if (originTypeLower.contains("float") || originTypeLower.contains("double") || originTypeLower.contains("dec") || originTypeLower.contains("numeric") || originTypeLower.contains("number") || originTypeLower.contains("real")){
                return "float";
            } else if (originTypeLower.contains("bool")){
                return "boolean";
            } else {
                log.warn("没有找到映射类型：{}", originType);
                return originType;
            }
        }
        log.warn("类型映射输入为空");
        return "string";
    }

    /**
     * @description: 获取表名
     * @param: modelDetailMap
     * @param: modelBizName
     * @return: java.lang.String
     * @throws
     * @author yang xiong
     * @date 2025/6/28 01:53
     **/
    private String getTableName(Map<String, Object> modelDetailMap, String modelBizName){
        String queryType = "";
        String tableQuery = null;
        if(null != modelDetailMap.get("queryType")) {
            queryType = (String) modelDetailMap.get("queryType");
        }
        if(null != modelDetailMap.get("tableQuery")) {
            tableQuery = (String) modelDetailMap.get("tableQuery");
        }
        return "table_query".equalsIgnoreCase(queryType) ? tableQuery : modelBizName;
    }

    /**
     * @description: 获取视图
     * @param: modelDetailMap
     * @return: java.lang.String
     * @throws
     * @author yang xiong
     * @date 2025/6/28 01:52
     **/
    private String getView(Map<String, Object> modelDetailMap){
        String queryType = "";
        String sqlQuery = null;
        if(null != modelDetailMap.get("queryType")) {
            queryType = (String) modelDetailMap.get("queryType");
        }
        if(null != modelDetailMap.get("sqlQuery")) {
            sqlQuery = (String) modelDetailMap.get("sqlQuery");
        }
        return "table_query".equalsIgnoreCase(queryType) ? null : sqlQuery;
    }
}
