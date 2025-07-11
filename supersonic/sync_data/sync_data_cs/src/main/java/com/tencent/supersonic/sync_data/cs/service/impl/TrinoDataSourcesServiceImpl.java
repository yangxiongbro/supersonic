package com.tencent.supersonic.sync_data.cs.service.impl;

import com.tencent.supersonic.common.pojo.enums.EngineType;
import com.tencent.supersonic.headless.api.pojo.DBColumn;
import com.tencent.supersonic.headless.api.pojo.request.DatabaseReq;
import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;
import com.tencent.supersonic.headless.core.adaptor.db.DbAdaptorFactory;
import com.tencent.supersonic.headless.core.pojo.ConnectInfo;
import com.tencent.supersonic.sync_data.common.constants.TrinoConstants;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.exception.business.BusinessExceptionAssertResponseEnum;
import com.tencent.supersonic.sync_data.common.utils.TrinoUtils;
import com.tencent.supersonic.sync_data.cs.service.TrinoDataSourcesService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * <b><code>TrinoDataSourcesServiceImpl</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/5/28 15:15
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Slf4j
@Service
public class TrinoDataSourcesServiceImpl implements TrinoDataSourcesService {

    private JdbcTemplate trinoJdbcTemplate;

    private ConnectInfo trinoConnectInfo;

    public TrinoDataSourcesServiceImpl(JdbcTemplate trinoJdbcTemplate, ConnectInfo trinoConnectInfo) {
        this.trinoJdbcTemplate = trinoJdbcTemplate;
        this.trinoConnectInfo = trinoConnectInfo;
    }

    public Boolean syncDataSources(DatabaseResp resp) throws BaseException {
        boolean result = false;
        try {
            if(dropCatalogIfExist(resp)){
                String catalogName = TrinoUtils.getCatalogName(resp);
                executeUpdate(
                        String.format(TrinoConstants.CREATE_CATALOG_SQL_TEMP,
                                TrinoUtils.doubleQuoteIdentifiers(catalogName),
                                TrinoConstants.ENGINE_TYPE_CONNECTOR_NAME_MAP.get(resp.getType()),
                                "true",
                                resp.getUrl(),
                                resp.getUsername(),
                                resp.passwordDecrypt(),
                                EngineType.ORACLE.getName().equalsIgnoreCase(resp.getType()) ? "" : TrinoConstants.CREATE_CATALOG_SQL_TEMP_DECIMAL
                        )
                );
                result = true;
            }
        } catch (Exception e) {
            log.warn("syncDataSources Exception:{}", e);
            throw BusinessExceptionAssertResponseEnum.SYNC_DATA_SOURCES_2_TRINO_FAIL
                    .newException(resp.getName());
        }
        return result;
    }

    public Boolean dropCatalogIfExist(DatabaseResp resp) throws BaseException {
        boolean result;
        String catalogName = null;
        try {
            catalogName = TrinoUtils.getCatalogName(resp);
            if (!CollectionUtils.isEmpty(executeQueryForList(
                    String.format(TrinoConstants.SHOW_SPECIFY_CATALOG_SQL_TEMP, catalogName)))) {
                executeUpdate(String.format(TrinoConstants.DROP_CATALOG_SQL_TEMP,
                        TrinoUtils.doubleQuoteIdentifiers(catalogName)));
            }
            result = true;
        } catch (Exception e) {
            log.warn("dropCatalogIfExist Exception:{}", e);
            throw BusinessExceptionAssertResponseEnum.DROP_CATALOG_FAIL.newException(catalogName);
        }
        return result;
    }

    public List<String> getTables(DatabaseResp resp, String catalog, String db) throws SQLException {
        return DbAdaptorFactory.getEngineAdaptor(EngineType.TRINO.getName()).getTables(this.trinoConnectInfo, TrinoUtils.doubleQuoteIdentifiers(TrinoUtils.getCatalogName(resp)), TrinoUtils.doubleQuoteIdentifiers(db));
    }

    public List<DBColumn> getColumns(DatabaseResp resp, String catalog, String db, String table) throws SQLException {
        if(resp.getType().equals(EngineType.ORACLE.getName())){
            db = db.toLowerCase();
        }
        return DbAdaptorFactory.getEngineAdaptor(EngineType.TRINO.getName()).getColumns(this.trinoConnectInfo, TrinoUtils.getCatalogName(resp), db, table);
    }

    public DatabaseResp parse2TrinoDatabaseResp(DatabaseResp databaseResp) {
        databaseResp.setUrl(this.trinoConnectInfo.getUrl());
        databaseResp.setUsername(this.trinoConnectInfo.getUserName());
        databaseResp.setPassword(null);
        databaseResp.setType(EngineType.TRINO.getName());
        return databaseResp;
    }

    public List<Map<String, Object>> executeQueryForList(String sql) {
        log.info("executeQueryForList sql: {}", sql);
        List<Map<String, Object>> list = trinoJdbcTemplate.queryForList(sql);
        log.info("executeQueryForList size {}", list.size());
        return list;
    }

    public int executeUpdate(String sql) {
        log.info("executeUpdate sql: {}", sql);
        int rows = trinoJdbcTemplate.update(sql);
        log.info("executeUpdate affected {} rows", rows);
        return rows;
    }
}
