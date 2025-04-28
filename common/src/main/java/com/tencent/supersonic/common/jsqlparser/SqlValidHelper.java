package com.tencent.supersonic.common.jsqlparser;

import lombok.extern.slf4j.Slf4j;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.select.PlainSelect;
import org.apache.commons.collections.CollectionUtils;

import java.util.List;

/**
 * Sql Parser valid Helper
 */
@Slf4j
public class SqlValidHelper {

    /**
     * determine if two SQL statements are equal.
     *
     * @param thisSql
     * @param otherSql
     * @return
     */
    public static boolean equals(String thisSql, String otherSql) {
        // 1. select fields
        List<String> thisSelectFields = SqlSelectHelper.getSelectFields(thisSql);
        List<String> otherSelectFields = SqlSelectHelper.getSelectFields(otherSql);

        if (!CollectionUtils.isEqualCollection(thisSelectFields, otherSelectFields)) {
            return false;
        }

        // 2. all fields
        List<String> thisAllFields = SqlSelectHelper.getAllSelectFields(thisSql);
        List<String> otherAllFields = SqlSelectHelper.getAllSelectFields(otherSql);

        if (!CollectionUtils.isEqualCollection(thisAllFields, otherAllFields)) {
            return false;
        }

        // 3. where
        List<FieldExpression> thisFieldExpressions = SqlSelectHelper.getFilterExpression(thisSql);
        List<FieldExpression> otherFieldExpressions = SqlSelectHelper.getFilterExpression(otherSql);

        if (!CollectionUtils.isEqualCollection(thisFieldExpressions, otherFieldExpressions)) {
            return false;
        }
        // 4. tableName
        if (!SqlSelectHelper.getDbTableName(thisSql)
                .equalsIgnoreCase(SqlSelectHelper.getDbTableName(otherSql))) {
            return false;
        }
        // 5. having
        List<FieldExpression> thisHavingExpressions = SqlSelectHelper.getHavingExpressions(thisSql);
        List<FieldExpression> otherHavingExpressions =
                SqlSelectHelper.getHavingExpressions(otherSql);

        if (!CollectionUtils.isEqualCollection(thisHavingExpressions, otherHavingExpressions)) {
            return false;
        }
        // 6. orderBy
        List<FieldExpression> thisOrderByExpressions =
                SqlSelectHelper.getOrderByExpressions(thisSql);
        List<FieldExpression> otherOrderByExpressions =
                SqlSelectHelper.getOrderByExpressions(otherSql);

        if (!CollectionUtils.isEqualCollection(thisOrderByExpressions, otherOrderByExpressions)) {
            return false;
        }
        return true;
    }

    public static boolean isValidSQL(String sql) {
        try {
            CCJSqlParserUtil.parse(sql);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public static boolean isComplexSQL(String sql) {
        List<PlainSelect> plainSelect = SqlSelectHelper.getPlainSelect(sql);
        return !CollectionUtils.isEmpty(plainSelect) && plainSelect.size() >= 2;
    }
}
