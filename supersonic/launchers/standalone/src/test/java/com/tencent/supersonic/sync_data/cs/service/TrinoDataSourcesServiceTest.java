package com.tencent.supersonic.sync_data.cs.service;

import com.tencent.supersonic.BaseApplication;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.common.pojo.enums.EngineType;
import com.tencent.supersonic.headless.api.pojo.request.DatabaseReq;
import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;
import com.tencent.supersonic.headless.server.service.DatabaseService;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import java.util.Map;

public class TrinoDataSourcesServiceTest extends BaseApplication {

    @Autowired
    private JdbcTemplate trinoJdbcTemplate;

    @Autowired
    private TrinoDataSourcesService trinoDataSourcesService;

    @Autowired
    private DatabaseService databaseService;

//    public TrinoDataSourcesServiceTest(JdbcTemplate trinoJdbcTemplate, TrinoDataSourcesService trinoDataSourcesService) {
//        this.trinoJdbcTemplate = trinoJdbcTemplate;
//        this.trinoDataSourcesService = trinoDataSourcesService;
//    }

    @Test
    public void test() {
        System.out.println("test");
        List<Map<String, Object>> resultList = trinoJdbcTemplate.queryForList("show catalogs");
        for(Map<String, Object> result : resultList){
            System.out.println(result);
        }
    }

    @Test
    public void syncDataSources() throws BaseException {
        DatabaseResp resp = new DatabaseResp();
        resp.setId(1L);
        resp.setName("soc_pg");
        resp.setType(EngineType.POSTGRESQL.toString());
        resp.setUrl("jdbc:postgresql://192.168.16.97:5432/soc?currentSchema=public&useUnicode=true&characterEncoding=utf8");
        resp.setUsername("postgres");
        resp.setPassword("/zBMngmvgpEg85CzMBhO1Q==");
        Boolean result = trinoDataSourcesService.syncDataSources(resp);
        System.out.println(result);
    }

    @Test
    public void syncDataSources2() throws BaseException {
        User user = new User();
        user.setName("Admin");
        user.setIsAdmin(1);
        for(Long id : databaseService.getDatabaseList(user).stream().map(DatabaseResp::getId).toList()){
            Boolean result = trinoDataSourcesService.syncDataSources(databaseService.getDatabase(id));
            System.out.println(result);
        }
    }

    @Test
    public void syncDataSources3() throws BaseException {
        Boolean result = trinoDataSourcesService.syncDataSources(databaseService.getDatabase(0L));
        System.out.println(result);
    }

}
