package com.tencent.supersonic.sync_data.cs.service;

import com.tencent.supersonic.headless.api.pojo.response.ModelResp;
import com.tencent.supersonic.sync_data.common.dto.SchemaDTO;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;

import java.util.List;

/**
 * <b><code>PandasAiSchemaService</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 11:39
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public interface PandasAiSchemaService {

    /**
     * @description: 模型信息转schema信息
     * @param: modelIdList
     * @return: List<SchemaDTO>
     * @throws
     * @author yang xiong
     * @date 2025/6/13 18:17
     **/
    List<SchemaDTO> getSchemaInfos(List<Long> modelIdList);

    /**
     * @description: 创建schema
     * @param: modelIdList
     * @return: java.lang.Integer
     * @throws
     * @author yang xiong
     * @date 2025/7/9 15:27
     **/
    Integer createSchemaByModelId(List<Long> modelIdList) throws BaseException;

    /**
     * @description: 创建schema
     * @param: dbResp
     * @param: modelRespList
     * @return: Integer
     * @throws
     * @author yang xiong
     * @date 2025/6/3 15:05
     **/
    Integer createSchema(List<ModelResp> modelRespList) throws BaseException;

    /**
     * @description: 删除schema
     * @param: modelIdList
     * @return: Integer
     * @throws
     * @author yang xiong
     * @date 2025/6/3 15:05
     **/
    Integer deleteSchema(List<Long> modelIdList) throws BaseException;

    /**
     * @description: 更新schema
     * @param: modelIdList
     * @return: Integer
     * @throws
     * @author yang xiong
     * @date 2025/6/5 17:44
     **/
    Integer updateSchema(List<Long> modelIdList) throws BaseException;
}
