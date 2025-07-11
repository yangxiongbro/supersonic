package com.tencent.supersonic.sync_data.cs.mapper;

import com.tencent.supersonic.sync_data.common.vo.DimensionVO;
import com.tencent.supersonic.sync_data.common.vo.MetricVO;
import com.tencent.supersonic.sync_data.common.vo.ModelRelaVO;
import com.tencent.supersonic.sync_data.common.vo.ModelVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * <b><code>PandasAiSchemaMapper</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 11:03
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Repository
@Mapper
public interface PandasAiSchemaMapper {

    /**
     * @description: 查询模型信息
     * @param: modelIdList
     * @return: List<ModelVO>
     * @throws
     * @author yang xiong
     * @date 2025/6/13 11:33
     **/
    List<ModelVO> listModel(@Param("modelIdList") List<Long> modelIdList);

    /**
     * @description: 查询模型维度信息
     * @param: modelIdList
     * @return: List<DimensionVO>
     * @throws
     * @author yang xiong
     * @date 2025/6/13 11:33
     **/
    List<DimensionVO> listDimension(@Param("modelIdList") List<Long> modelIdList);

    /**
     * @description: 查询模型度量信息
     * @param: modelIdList
     * @return: List<MetricVO>
     * @throws
     * @author yang xiong
     * @date 2025/6/13 11:33
     **/
    List<MetricVO> listMetric(@Param("modelIdList") List<Long> modelIdList);

    /**
     * @description: 查询模型关联信息
     * @param: modelIdList
     * @return: List<MetricVO>
     * @throws
     * @author yang xiong
     * @date 2025/6/13 11:33
     **/
    List<ModelRelaVO> listModelRela(@Param("modelIdList") List<Long> modelIdList);
}
