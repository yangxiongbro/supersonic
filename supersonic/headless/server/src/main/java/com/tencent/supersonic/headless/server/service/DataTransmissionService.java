package com.tencent.supersonic.headless.server.service;

import com.tencent.supersonic.headless.server.dto.DataTransmissionDTO;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;

import java.util.List;

/**
 * <b><code>DataTransmissionService</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/3 17:25
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
public interface DataTransmissionService {
    DataTransmissionDTO exportData(Long domainId, List<Long> dataSetIdList);

    Boolean importData(Long domainId, Long databaseId, DataTransmissionDTO data) throws BaseException;
}
