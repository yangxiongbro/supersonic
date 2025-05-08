package com.tencent.supersonic.headless.core.adaptor.db;

import com.tencent.supersonic.common.pojo.Constants;
import com.tencent.supersonic.common.pojo.enums.TimeDimensionEnum;

public class OracleAdaptor extends BaseDbAdaptor {
    @Override
    public String getDateFormat(String dateType, String dateFormat, String column) {
        String toDateSql = null;
        String toCharSql = null;
        if (dateFormat.equalsIgnoreCase(Constants.DAY_FORMAT_INT)) {
            toDateSql = "TO_DATE(%s, 'yyyymmdd')";
        } else if (dateFormat.equalsIgnoreCase(Constants.DAY_FORMAT)) {
            toDateSql = "TO_DATE(%s, 'yyyy-mm-dd')";
        }
        if (TimeDimensionEnum.MONTH.name().equalsIgnoreCase(dateType)) {
            toCharSql = "TO_CHAR(%s, 'yyyy-mm')";
        } else if (TimeDimensionEnum.WEEK.name().equalsIgnoreCase(dateType)) {
            toCharSql = "TO_CHAR(TRUNC(%s, 'IW'), 'yyyy-mm-dd')";
        } else {
            toCharSql = "TO_CHAR(%s, 'yyyy-mm-dd')";
        }
        if(null == toDateSql || null == toCharSql){
            return column;
        }
        return toCharSql.replace("%s", toDateSql.replace("%s", column));
    }

    @Override
    public String rewriteSql(String sql) {
        return sql;
    }
}
