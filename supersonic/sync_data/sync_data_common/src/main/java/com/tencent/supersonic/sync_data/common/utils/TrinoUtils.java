package com.tencent.supersonic.sync_data.common.utils;

import com.tencent.supersonic.headless.api.pojo.response.DatabaseResp;

/**
 * <b><code>TrinoUtils</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/13 16:41
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public class TrinoUtils {

    public static String doubleQuoteIdentifiers(String identifiers){
        return String.format("\"%s\"", identifiers.trim());
    }

    public static String doubleQuoteEachIdentifiers(String identifiersStr){
        String[] identifiers = identifiersStr.trim().split("\\.");
        for(int i = 0; i < identifiers.length; i++){
            identifiers[i] = doubleQuoteIdentifiers(identifiers[i]);
        }
        return String.join(".", identifiers);
    }

    public static String getCatalogName(DatabaseResp resp){
        return getCatalogName(resp.getId());
    }

    public static String getCatalogName(Long databaseId){
        return "db_"+databaseId;
    }
}
