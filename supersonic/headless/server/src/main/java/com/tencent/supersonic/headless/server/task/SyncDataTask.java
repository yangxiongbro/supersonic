package com.tencent.supersonic.headless.server.task;

import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.api.pojo.MetaFilter;
import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;
import com.tencent.supersonic.headless.api.pojo.response.ModelResp;
import com.tencent.supersonic.headless.server.service.DatabaseService;
import com.tencent.supersonic.headless.server.service.ModelService;
import com.tencent.supersonic.sync_data.cs.service.PandasAiSchemaService;
import com.tencent.supersonic.sync_data.cs.service.TrinoDataSourcesService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * <b><code>SyncDataTask</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/18 14:53
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Slf4j
@Component
public class SyncDataTask implements CommandLineRunner {

    private DatabaseService databaseService;

    private ModelService modelService;

    private TrinoDataSourcesService trinoDataSourcesService;

    private PandasAiSchemaService pandasAiSchemaService;

    @Value("${SYNC_DATA_WHEN_START_UP:false}")
    private Boolean syncDataWhenStartUp;

    public SyncDataTask(DatabaseService databaseService, ModelService modelService, TrinoDataSourcesService trinoDataSourcesService, PandasAiSchemaService pandasAiSchemaService){
        this.databaseService = databaseService;
        this.modelService = modelService;
        this.trinoDataSourcesService = trinoDataSourcesService;
        this.pandasAiSchemaService = pandasAiSchemaService;
    }

    @Override
    public void run(String... args) throws Exception {
        if(!Boolean.TRUE.equals(syncDataWhenStartUp)){
            log.info("syncDataWhenStartUp is false");
            return;
        }
        Thread.sleep(10000);
        User user = new User();
        user.setName("Admin");
        user.setIsAdmin(1);
        for(Long id : databaseService.getDatabaseList(user).stream().map(DatabaseResp::getId).toList()){
            try {
                Boolean result = trinoDataSourcesService.syncDataSources(databaseService.getDatabase(id));
                log.info("sync data sources result:{}", result);
            } catch (Exception e) {
                log.info("sync data sources exception:{}", e);
            }
        }
        List<ModelResp> modelRespList = modelService.getModelList(new MetaFilter());
        try {
            Integer result = pandasAiSchemaService.createSchema(modelRespList);
            log.info("create schema result:{}", result);
        } catch (Exception e) {
            log.info("create schema result:{}", e);
        }
    }
}
