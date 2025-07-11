package com.tencent.supersonic.sync_data.cs.service;

import com.tencent.supersonic.headless.api.pojo.DBColumn;
import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;

import java.sql.SQLException;
import java.util.List;

/**
 * <b><code>TrinoDataSourcesService</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/5/28 15:15
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public interface TrinoDataSourcesService {

    /**
     * @description: 同步数据源到trino
     * @param: resp
     * @return: Boolean
     * @throws
     * @author yang xiong
     * @date 2025/5/28 15:14
     **/
    Boolean syncDataSources(DatabaseResp resp) throws BaseException;

    /**
     * @description: 删除catalog
     * @param: resp
     * @return: Boolean
     * @throws
     * @author yang xiong
     * @date 2025/6/3 18:07
     **/
    Boolean dropCatalogIfExist(DatabaseResp resp) throws BaseException;

    /**
     * @description: 获取表名
     * @param: resp
     * @param: catalog
     * @param: db
     * @return: List<String>
     * @throws SQLException
     * @author yang xiong
     * @date 2025/5/28 17:39
     **/
    List<String> getTables(DatabaseResp resp, String catalog, String db) throws SQLException;

    /**
     * @description: 获取表字段
     * @param: resp
     * @param: catalog
     * @param: db
     * @param: table
     * @return: List<String>
     * @throws SQLException
     * @author yang xiong
     * @date 2025/5/28 17:54
     **/
    List<DBColumn> getColumns(DatabaseResp resp, String catalog, String db, String table) throws SQLException;

    DatabaseResp parse2TrinoDatabaseResp(DatabaseResp databaseResp);

}
