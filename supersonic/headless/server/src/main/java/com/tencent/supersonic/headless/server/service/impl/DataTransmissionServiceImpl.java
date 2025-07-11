package com.tencent.supersonic.headless.server.service.impl;

import com.alibaba.fastjson2.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.tencent.supersonic.common.pojo.enums.StatusEnum;
import com.tencent.supersonic.headless.api.pojo.DataSetDetail;
import com.tencent.supersonic.headless.api.pojo.DataSetModelConfig;
import com.tencent.supersonic.headless.api.pojo.response.TermResp;
import com.tencent.supersonic.headless.server.dto.*;
import com.tencent.supersonic.headless.server.persistence.dataobject.*;
import com.tencent.supersonic.headless.server.persistence.repository.DimensionRepository;
import com.tencent.supersonic.headless.server.persistence.repository.MetricRepository;
import com.tencent.supersonic.headless.server.persistence.repository.ModelRepository;
import com.tencent.supersonic.headless.server.pojo.DimensionFilter;
import com.tencent.supersonic.headless.server.pojo.MetricFilter;
import com.tencent.supersonic.headless.server.pojo.ModelFilter;
import com.tencent.supersonic.headless.server.service.*;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.exception.business.BusinessExceptionAssertResponseEnum;
import com.tencent.supersonic.sync_data.common.utils.TrinoUtils;
import com.tencent.supersonic.sync_data.cs.service.PandasAiSchemaService;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.util.*;
import java.util.stream.Collectors;

/**
 * <b><code>DataTransmissionServiceImpl</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/3 17:25
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Service
public class DataTransmissionServiceImpl implements DataTransmissionService {
    @Autowired
    private DataSetService dataSetService;
    @Autowired
    private ModelRepository modelRepository;
    @Autowired
    private DimensionRepository dimensionRepository;
    @Autowired
    private MetricRepository metricRepository;
    @Autowired
    private ModelRelaService modelRelaService;
    @Autowired
    private TermService termService;
    @Autowired
    private PandasAiSchemaService pandasAiSchemaService;

    public DataTransmissionDTO exportData(Long domainId, List<Long> dataSetIdList) {
        List<DataSetDO> dataSetList = dataSetService.listDo(new QueryWrapper<DataSetDO>().lambda()
                .eq(DataSetDO::getDomainId, domainId)
                .in(!CollectionUtils.isEmpty(dataSetIdList), DataSetDO::getId, dataSetIdList)
                .ne(DataSetDO::getStatus, StatusEnum.DELETED.getCode()));
        for(DataSetDO dataSetDO : dataSetList) {
            dataSetDO.setId(null);
            dataSetDO.setDomainId(null);
        }

        List<ModelRelaDO> modelRelaList = modelRelaService.listDo(new QueryWrapper<ModelRelaDO>().lambda()
                .eq(ModelRelaDO::getDomainId, domainId));
        for(ModelRelaDO modelRelaDO: modelRelaList){
            modelRelaDO.setId(null);
            modelRelaDO.setDomainId(null);
        }

        ModelFilter modelFilter = new ModelFilter();
        modelFilter.setDomainId(domainId);
        List<ModelDO> modelList = modelRepository.getModelList(modelFilter);
        List<ModelDTO> modelDTOList = new ArrayList<>(modelList.size());
        List<Long> modelIdList = new ArrayList<>(modelList.size());
        for(ModelDO modelDO: modelList){
            ModelDTO dto = new ModelDTO();
            BeanUtils.copyProperties(modelDO, dto);
            dto.setDatabaseId(null);
            dto.setId(null);
            dto.setDomainId(null);
            dto.setOriginId(modelDO.getId());
            modelDTOList.add(dto);
            modelIdList.add(modelDO.getId());
        }

        List<DimensionDTO> dimensionDTOList = Collections.emptyList();
        if(!CollectionUtils.isEmpty(modelIdList)){
            DimensionFilter dimensionFilter = new DimensionFilter();
            dimensionFilter.setModelIds(modelIdList);
            List<DimensionDO> dimensionList = dimensionRepository.getDimension(dimensionFilter);
            dimensionDTOList = new ArrayList<>(dimensionList.size());
            for(DimensionDO dimensionDO: dimensionList){
                DimensionDTO dto = new DimensionDTO();
                BeanUtils.copyProperties(dimensionDO, dto);
                dto.setId(null);
                dto.setOriginId(dimensionDO.getId());
                dimensionDTOList.add(dto);
            }
        }

        List<MetricDTO> metricDTOList = Collections.emptyList();
        if(!CollectionUtils.isEmpty(modelIdList)) {
            MetricFilter metricFilter = new MetricFilter();
            metricFilter.setModelIds(modelIdList);
            List<MetricDO> metricList = metricRepository.getMetric(metricFilter);
            metricDTOList = new ArrayList<>(metricList.size());
            for (MetricDO metricDO : metricList) {
                MetricDTO dto = new MetricDTO();
                BeanUtils.copyProperties(metricDO, dto);
                dto.setId(null);
                dto.setOriginId(metricDO.getId());
                metricDTOList.add(dto);
            }
        }

        List<TermDO> termList = termService.listDo(new QueryWrapper<TermDO>().lambda()
                .eq(TermDO::getDomainId, domainId));
        for(TermDO termDO: termList){
            termDO.setId(null);
            termDO.setDomainId(null);
        }

        return new DataTransmissionDTO(dataSetList, modelDTOList, modelRelaList, dimensionDTOList, metricDTOList, termList);
    }

    public Boolean importData(Long domainId, Long databaseId, DataTransmissionDTO data) throws BaseException {
        List<DataSetDO> dataSetDOList = Optional.ofNullable(data.getDataSetList()).orElse(Collections.emptyList());
        List<ModelDTO> modelDTOList = Optional.ofNullable(data.getModelList()).orElse(Collections.emptyList());
        List<ModelRelaDO> modelRelaDOList = Optional.ofNullable(data.getModelRelaList()).orElse(Collections.emptyList());
        List<DimensionDTO> dimensionDTOList = Optional.ofNullable(data.getDimensionList()).orElse(Collections.emptyList());
        List<MetricDTO> metricDTOList = Optional.ofNullable(data.getMetricList()).orElse(Collections.emptyList());
        List<TermDO> termDOList = Optional.ofNullable(data.getTermList()).orElse(Collections.emptyList());
        // 保存模型
        if(!CollectionUtils.isEmpty(modelDTOList)){
            List<ModelDO> modelDOList = new ArrayList<>(modelDTOList.size());
            for(ModelDTO dto: modelDTOList) {
                dto.setDatabaseId(databaseId);
                dto.setDomainId(domainId);
                String modelDetail = dto.getModelDetail();
                if(null != modelDetail){
                    dto.setModelDetail(dto.getModelDetail().replaceAll("db_[0-9]+\\.", TrinoUtils.getCatalogName(databaseId)+"."));
                }
                modelDOList.add(dto);
            }
            modelRepository.batchCreate(modelDOList);
        }
        // 旧新模型id映射
        List<Long> newModelIdList = new ArrayList<>(modelDTOList.size());
        Map<Long, Long> modelIdMap = new HashMap<>(modelDTOList.size());
        for(ModelDTO dto: modelDTOList){
            newModelIdList.add(dto.getId());
            modelIdMap.put(dto.getOriginId(), dto.getId());
        }
        // 保存关联关系
        if(!CollectionUtils.isEmpty(modelRelaDOList)){
            for(ModelRelaDO modelRelaDO: modelRelaDOList){
                modelRelaDO.setFromModelId(getNewModelId(modelIdMap, modelRelaDO.getFromModelId()));
                modelRelaDO.setToModelId(getNewModelId(modelIdMap, modelRelaDO.getToModelId()));
                modelRelaDO.setDomainId(domainId);
            }
            modelRelaService.batchSave(modelRelaDOList);
        }
        // 保存维度
        if(!CollectionUtils.isEmpty(dimensionDTOList)){
            List<DimensionDO> dimensionDOList = new ArrayList<>(dimensionDTOList.size());
            for(DimensionDTO dto: dimensionDTOList){
                dto.setModelId(getNewModelId(modelIdMap, dto.getModelId()));
                dimensionDOList.add(dto);
            }
            dimensionRepository.createDimensionBatch(dimensionDOList);
        }
        Map<Long, Long> dimensionIdMap = dimensionDTOList.stream()
                .collect(Collectors.toMap(DimensionDTO::getOriginId, DimensionDTO::getId, (key1, key2) -> key2));

        // 保存度量
        if(!CollectionUtils.isEmpty(metricDTOList)){
            List<MetricDO> metricDOList = new ArrayList<>(metricDTOList.size());
            for(MetricDTO dto: metricDTOList){
                dto.setModelId(getNewModelId(modelIdMap, dto.getModelId()));
                metricDOList.add(dto);
            }
            metricRepository.createMetricBatch(metricDOList);
        }
        Map<Long, Long> metricIdMap = metricDTOList.stream()
                .collect(Collectors.toMap(MetricDTO::getOriginId, MetricDTO::getId, (key1, key2) -> key2));

        // 保存术语
        if(!CollectionUtils.isEmpty(termDOList)){
            Set<String> termNameList = termService.getTerms(domainId, null).stream().map(TermResp::getName).collect(Collectors.toSet());
            List<TermDO> termDOUniqueList = new ArrayList<>(termDOList.size());
            for(TermDO termDO: termDOList){
                if(termNameList.contains(termDO.getName())){
                   continue;
                }
                termDO.setDomainId(domainId);
                termDOUniqueList.add(termDO);
            }
            termService.batchSave(termDOUniqueList);
        }

        // 保存数据集
        if(!CollectionUtils.isEmpty(dataSetDOList)){
            for(DataSetDO dataSetDO: dataSetDOList) {
                dataSetDO.setDomainId(domainId);
                DataSetDetail dataSetDetail = JSONObject.parseObject(dataSetDO.getDataSetDetail(), DataSetDetail.class);
                if(null != dataSetDetail && !CollectionUtils.isEmpty(dataSetDetail.getDataSetModelConfigs())){
                    for(DataSetModelConfig config: dataSetDetail.getDataSetModelConfigs()){
                        // 更新模型id
                        config.setId(getNewModelId(modelIdMap, config.getId()));
                        // 更新维度id
                        if(!CollectionUtils.isEmpty(config.getDimensions())){
                            List<Long> idList = new ArrayList<>(config.getDimensions().size());
                            for(Long id: config.getDimensions()){
                                idList.add(getNewModelId(dimensionIdMap, id));
                            }
                            config.setDimensions(idList);
                        }
                        // 更新度量id
                        if(!CollectionUtils.isEmpty(config.getMetrics())){
                            List<Long> idList = new ArrayList<>(config.getMetrics().size());
                            for(Long id: config.getMetrics()){
                                idList.add(getNewModelId(metricIdMap, id));
                            }
                            config.setMetrics(idList);
                        }
                    }
                    dataSetDO.setDataSetDetail(JSONObject.toJSONString(dataSetDetail));
                }
            }
            dataSetService.batchSave(dataSetDOList);
        }

        // 同步pandas-ai schema
        pandasAiSchemaService.createSchemaByModelId(newModelIdList);
        return true;
    }

    private Long getNewModelId(Map<Long, Long> modelIdMap, Long originModelId) throws BaseException {
        if(null == originModelId){
            return null;
        }
        Long newModelId = modelIdMap.get(originModelId);
        BusinessExceptionAssertResponseEnum.THROW_EXCEPTION.assertFalse(null == newModelId, String.format("没有找到模型id:%d对应的模型id", originModelId));
        return newModelId;
    }

}
