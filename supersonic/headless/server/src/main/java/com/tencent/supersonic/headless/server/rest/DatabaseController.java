package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.api.pojo.DBColumn;
import com.tencent.supersonic.headless.api.pojo.request.DatabaseReq;
import com.tencent.supersonic.headless.api.pojo.request.ModelBuildReq;
import com.tencent.supersonic.headless.api.pojo.request.SqlExecuteReq;
import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;
import com.tencent.supersonic.headless.api.pojo.response.SemanticQueryResp;
import com.tencent.supersonic.headless.server.pojo.DatabaseParameter;
import com.tencent.supersonic.headless.server.service.DatabaseService;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.cs.service.TrinoDataSourcesService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/semantic/database")
public class DatabaseController {

    private DatabaseService databaseService;

    private TrinoDataSourcesService trinoDataSourcesService;

    public DatabaseController(DatabaseService databaseService, TrinoDataSourcesService trinoDataSourcesService) {
        this.databaseService = databaseService;
        this.trinoDataSourcesService = trinoDataSourcesService;
    }

    @PostMapping("/testConnect")
    public boolean testConnect(@RequestBody DatabaseReq databaseReq, HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return databaseService.testConnect(databaseReq, user);
    }

    @PostMapping("/createOrUpdateDatabase")
    @Transactional(rollbackFor = Exception.class)
    public DatabaseResp createOrUpdateDatabase(@RequestBody DatabaseReq databaseReq,
            HttpServletRequest request, HttpServletResponse response) throws BaseException {
        User user = UserHolder.findUser(request, response);
        DatabaseResp resp = databaseService.createOrUpdateDatabase(databaseReq, user);
        trinoDataSourcesService.syncDataSources(resp);
        return resp;
    }

    @GetMapping("/{id}")
    public DatabaseResp getDatabase(@PathVariable("id") Long id, HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return databaseService.getDatabase(id, user);
    }

    @GetMapping("/getDatabaseList")
    public List<DatabaseResp> getDatabaseList(HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        List<DatabaseResp> list = databaseService.getDatabaseList(user);
        list.forEach(item -> item.setName(String.format("%s（db_%d）", item.getName(), item.getId())));
        return list;
    }

    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteDatabase(@PathVariable("id") Long id) throws BaseException {
        DatabaseResp dbResp = databaseService.getDatabase(id);
        databaseService.deleteDatabase(id);
        trinoDataSourcesService.dropCatalogIfExist(dbResp);
        return true;
    }

    @PostMapping("/executeSql")
    public SemanticQueryResp executeSql(@RequestBody SqlExecuteReq sqlExecuteReq,
            HttpServletRequest request, HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return databaseService.executeSql(sqlExecuteReq, user);
    }

    @RequestMapping("/getCatalogs")
    public List<String> getCatalogs(@RequestParam("id") Long databaseId) throws SQLException {
        return databaseService.getCatalogs(databaseId);
    }

    @RequestMapping("/getDbNames")
    public List<String> getDbNames(@RequestParam("id") Long databaseId,
            @RequestParam(value = "catalog", required = false) String catalog) throws SQLException {
        return databaseService.getDbNames(databaseId, catalog);
    }

    @RequestMapping("/getTables")
    public List<String> getTables(@RequestParam("databaseId") Long databaseId,
            @RequestParam(value = "catalog", required = false) String catalog,
            @RequestParam("db") String db) throws SQLException {
        return trinoDataSourcesService.getTables(databaseService.getDatabase(databaseId), catalog, db);
//        return databaseService.getTables(databaseId, catalog, db);
    }

    @RequestMapping("/getColumnsByName")
    public List<DBColumn> getColumnsByName(@RequestParam("databaseId") Long databaseId,
            @RequestParam(name = "catalog", required = false) String catalog,
            @RequestParam("db") String db, @RequestParam("table") String table)
            throws SQLException {
        return trinoDataSourcesService.getColumns(databaseService.getDatabase(databaseId), catalog, db, table);
//        return databaseService.getColumns(databaseId, catalog, db, table);
    }

    @PostMapping("/listColumnsBySql")
    public List<DBColumn> listColumnsBySql(@RequestBody ModelBuildReq modelBuildReq)
            throws SQLException {
        return databaseService.getColumns(modelBuildReq.getDatabaseId(), modelBuildReq.getSql());
    }

    @GetMapping("/getDatabaseParameters")
    public Map<String, List<DatabaseParameter>> getDatabaseParameters(HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return databaseService.getDatabaseParameters(user);
    }
}
