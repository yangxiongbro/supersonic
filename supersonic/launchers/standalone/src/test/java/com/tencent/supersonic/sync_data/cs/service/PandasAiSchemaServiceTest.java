package com.tencent.supersonic.sync_data.cs.service;

import com.tencent.supersonic.BaseApplication;
import com.tencent.supersonic.headless.api.pojo.MetaFilter;
import com.tencent.supersonic.headless.api.pojo.response.ModelResp;
import com.tencent.supersonic.headless.server.service.ModelService;
import com.tencent.supersonic.sync_data.common.dto.SchemaDTO;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.Collections;
import java.util.List;
import java.util.stream.Stream;

/**
 * <b><code>TestPandasAiSchemaService</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 14:34
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public class PandasAiSchemaServiceTest extends BaseApplication {
    @Autowired
    private PandasAiSchemaService pandasAiSchemaService;

    @Autowired
    private ModelService modelService;

    @Test
    public void getSchemaInfos() {
        List<SchemaDTO> schemaDTOList = pandasAiSchemaService.getSchemaInfos(Collections.singletonList(3L));
        schemaDTOList.forEach(System.out::println);
    }

    @Test
    public void createSchema() throws BaseException {
        ModelResp modelResp34 = new ModelResp(); modelResp34.setId(34L);

        List<ModelResp> modelRespList = Stream.of(
                modelResp34
        ).toList();
//        modelRespList = modelService.getModelList(new MetaFilter());
        Integer result = pandasAiSchemaService.createSchema(modelRespList);
        System.out.println(result);
    }

    @Test
    public void deleteSchema() throws BaseException {
        List<Long> modelIdList = Stream.of(
                8L
        ).toList();
        Integer result = pandasAiSchemaService.deleteSchema(modelIdList);
        System.out.println(result);
    }

    @Test
    public void updateSchema() throws BaseException {
        List<Long> modelIdList = Stream.of(
                8L
        ).toList();
        Integer result = pandasAiSchemaService.updateSchema(modelIdList);
        System.out.println(result);
    }
}
