package com.tencent.supersonic.headless.server.dto;

import com.tencent.supersonic.headless.server.persistence.dataobject.DataSetDO;
import com.tencent.supersonic.headless.server.persistence.dataobject.ModelRelaDO;
import com.tencent.supersonic.headless.server.persistence.dataobject.TermDO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * <b><code>DataTransmissionDTO</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/9 16:03
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class DataTransmissionDTO {
    List<DataSetDO> dataSetList;

    List<ModelDTO> modelList;

    List<ModelRelaDO> modelRelaList;

    List<DimensionDTO> dimensionList;

    List<MetricDTO> metricList;

    List<TermDO> termList;

}
