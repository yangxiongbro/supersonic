package com.tencent.supersonic.sync_data.common.constants;

import com.tencent.supersonic.common.pojo.ChatApp;
import com.tencent.supersonic.common.pojo.enums.AppModule;
import com.tencent.supersonic.common.pojo.enums.EngineType;
import com.tencent.supersonic.headless.chat.corrector.LLMSqlCorrector;
import com.tencent.supersonic.headless.chat.parser.llm.OnePassSCSqlGenStrategy;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;

import java.util.*;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toMap;

/**
 * <b><code>TrinoConstants</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/5/28 15:15
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public class TrinoConstants {
    private TrinoConstants(){}

    public static final String CREATE_CATALOG_SQL_TEMP =
            "CREATE CATALOG %s USING %s \n" +
            "WITH (\n" +
            "  \"case-insensitive-name-matching\" = '%s', \n" +
            "  \"connection-url\" = '%s', \n" +
            "  \"connection-user\" = '%s', \n" +
            "  \"connection-password\" = '%s' \n" +
            "  %s " +
            ")";

    public static final String CREATE_CATALOG_SQL_TEMP_DECIMAL =
            "  , \n" +
            "  \"decimal-mapping\" = 'allow_overflow', \n" +
            "  \"decimal-default-scale\" = '15' \n";

    public static final String DROP_CATALOG_SQL_TEMP =
            "DROP CATALOG %s";

    public static final String SHOW_SPECIFY_CATALOG_SQL_TEMP =
            "SHOW CATALOGS LIKE '%s'";

    public static final Map<String, String> ENGINE_TYPE_CONNECTOR_NAME_MAP = Stream.of(EngineType.values())
            .map(type -> new AbstractMap.SimpleEntry<>(type.name(), type.name().toLowerCase()))
            .collect(toMap(AbstractMap.SimpleEntry::getKey, AbstractMap.SimpleEntry::getValue));;

    public static final String TRINO_IDENTIFIERS_QUOTES = "\"";

    public static final HttpHeaders POST_HEADERS;
    static {
        POST_HEADERS = new HttpHeaders();
        POST_HEADERS.add(HttpHeaders.USER_AGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36");
        POST_HEADERS.setContentType(MediaType.APPLICATION_JSON);
        POST_HEADERS.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));
    }

    public static final HttpHeaders CONTENT_JSON_ACCEPT_TEXT_HEADERS;
    static {
        CONTENT_JSON_ACCEPT_TEXT_HEADERS = new HttpHeaders();
        CONTENT_JSON_ACCEPT_TEXT_HEADERS.add(HttpHeaders.USER_AGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36");
        CONTENT_JSON_ACCEPT_TEXT_HEADERS.setContentType(MediaType.APPLICATION_JSON);
        CONTENT_JSON_ACCEPT_TEXT_HEADERS.setAccept(Collections.singletonList(MediaType.TEXT_PLAIN));
    }

    public static final Map<String, String> TYPE_MAPPING_MAP = Stream.of(
            new AbstractMap.SimpleEntry<>("int", "integer"),
            new AbstractMap.SimpleEntry<>("date", "datetime"),
            new AbstractMap.SimpleEntry<>("time", "datetime"),
            new AbstractMap.SimpleEntry<>("char", "string"),
            new AbstractMap.SimpleEntry<>("text", "string"),
            new AbstractMap.SimpleEntry<>("lob", "string"),
            new AbstractMap.SimpleEntry<>("json", "string"),
            new AbstractMap.SimpleEntry<>("xml", "string"),
            new AbstractMap.SimpleEntry<>("float", "float"),
            new AbstractMap.SimpleEntry<>("double", "float"),
            new AbstractMap.SimpleEntry<>("dec", "float"),
            new AbstractMap.SimpleEntry<>("numeric", "float"),
            new AbstractMap.SimpleEntry<>("number", "float"),
            new AbstractMap.SimpleEntry<>("real", "float"),
            new AbstractMap.SimpleEntry<>("bool", "boolean")
    ).collect(toMap(AbstractMap.SimpleEntry::getKey, AbstractMap.SimpleEntry::getValue));

    public static final List<Map<String,Object>> PANDAS_AI_NOT_DATA_RESPONSE = Collections.singletonList(
            Collections.singletonMap("结果", "暂无数据")
    );

    public static final Map<String, ChatApp> CHAT_INSTRUCTION_MAP = Stream.of(
                    new AbstractMap.SimpleEntry<>(OnePassSCSqlGenStrategy.APP_KEY,
                            ChatApp.builder()
                                    .prompt(
                                        "- 重要：在编写 SQL 时，如果表是由视图(View)表示的，要将表名替换为视图的SQL表达式\n" +
                                        "- 重要：在编写 SQL 时，如果column有设置expression，则在SQL必须使用expression代替字段名，否则会出错\n" +
                                        "- 在编写 SQL 时，查询返回的字段不要返回表示主键的ID字段。\n" +
                                        "- 在编写 SQL 时，为了中国用户易于理解返回数据列意思，请使用中文别名。\n" +
                                        "- 在编写 SQL 时，别名必须使用双引号包裹包括\n" +
                                        "- 在编写 SQL 时，必须严格遵循数据库方言以生成正确的 SQL 语法，尤其要重点关注所使用的 SQL 函数。\n" +
                                        "- 在编写 SQL 时，仅查询相关表，并通过 SQL 查询进行聚合、排序、连接和分组。\n" +
                                        "- 在编写 SQL 时，ORDER BY 子句中使用的字段名称应与 SELECT 部分定义的别名保持一致。\n" +
                                        "- 在编写 SQL 时，由于在涉及日期处理时，生成 SQL 语句经常会出错，因此必须先彻底研究“# SQL日期处理”部分的内容。\n" +
                                        "- 当db dialect是trino时：\n" +
                                        "- 如果日期字段为字符串类型，那么必须先转换为日期类型再进行处理，使用Trno的DATE_PARSE()函数进行处理：\n" +
                                        "  DATE_PARSE() 函数的基本用法：\n" +
                                        "  语法：DATE_PARSE(string, format)\n" +
                                        "  参数说明：\n" +
                                        "    * string：要解析的字符串（通常是日期时间格式的文本）\n" +
                                        "    * format：格式化模板字符串，使用标准的日期格式符号\n" +
                                        "  示例：\n" +
                                        "  1、SELECT DATE_PARSE('2025-06-17', '%Y-%m-%d') AS parsed_date;\n" +
                                        "    输出: DATE '2025-06-17'  \n" +
                                        "  2、SELECT DATE_PARSE('2025-06-17 14:30:45', '%Y-%m-%d %H:%i:%s') AS parsed_timestamp;\n" +
                                        "    输出: TIMESTAMP '2025-06-17 14:30:45' \n" +
                                        "- 在编写 SQL 时，在日期格式化函数中使用两个连续的百分号是错误的。例如，DATE_FORMAT(date_field, '%%Y-%%m') 是错误的。正确的格式应该使用单个百分号，例如 '%Y-%m'\n" +
                                        "- 将日期转为'月'时使用strftime(<日期字段>,'%Y-%m')，如果日期字段为字符串，则需要先转换：strftime(CAST(<日期字段> AS DATE),'%Y-%m')\n" +
                                        "- 将日期转为'日'时使用strftime(<日期字段>,'%Y-%m-%d')，如果日期字段为字符串，则需要先转换：strftime(CAST(<日期字段> AS DATE,'%Y-%m-%d'))\n" +
                                        "- 计算昨天(1天前)使用CURRENT_DATE - INTERVAL '1' day；计算前天(2天前)使用CURRENT_DATE - INTERVAL '2' day\n" +
                                        "- 计算N天前使用CURRENT_DATE - INTERVAL '<N>' day，例如计算6天前：CURRENT_DATE - INTERVAL '6' day\n" +
                                        "- 计算N天前使用CURRENT_DATE - INTERVAL '<N>' month，例如计算上个月：CURRENT_DATE - INTERVAL '1' month\n" +
                                        "- 计算N年前使用CURRENT_DATE - INTERVAL '<N>' year，例如计算上一年：CURRENT_DATE - INTERVAL '1' 年\n" +
                                        "- 表名前必须要指定catalog和schema")
                                    .name("语义SQL解析")
                                    .appModule(AppModule.CHAT)
                                    .description("通过大模型做语义解析生成S2SQL")
                                    .enable(true)
                                    .build()
                    ),
                    new AbstractMap.SimpleEntry<>(LLMSqlCorrector.APP_KEY,
                            ChatApp.builder().prompt(
                                    "- 重要：在编写 SQL 时，如果表是由视图(View)表示的，要将表名替换为视图的SQL表达式\n" +
                                    "- 重要：在编写 SQL 时，如果column有设置expression，则在SQL必须使用expression代替字段名，否则会出错\n" +
                                    "- 在编写 SQL 时，查询返回的字段不要返回表示主键的ID字段。\n" +
                                    "- 在编写 SQL 时，为了中国用户易于理解返回数据列意思，请使用中文别名。\n" +
                                    "- 在编写 SQL 时，必须严格遵循数据库方言以生成正确的 SQL 语法，尤其要重点关注所使用的 SQL 函数。\n" +
                                    "- 在编写 SQL 时，仅查询相关表，并通过 SQL 查询进行聚合、排序、连接和分组。\n" +
                                    "- 在编写 SQL 时，ORDER BY 子句中使用的字段名称应与 SELECT 部分定义的别名保持一致。\n" +
                                    "- 在编写 SQL 时，由于在涉及日期处理时，生成 SQL 语句经常会出错，因此必须先彻底研究“# SQL日期处理”部分的内容。\n" +
                                    "- 当db dialect是trino时：\n" +
                                    "- 如果日期字段为字符串类型，那么必须先转换为日期类型再进行处理，使用Trno的DATE_PARSE()函数进行处理：\n" +
                                    "  DATE_PARSE() 函数的基本用法：\n" +
                                    "  语法：DATE_PARSE(string, format)\n" +
                                    "  参数说明：\n" +
                                    "    * string：要解析的字符串（通常是日期时间格式的文本）\n" +
                                    "    * format：格式化模板字符串，使用标准的日期格式符号\n" +
                                    "  示例：\n" +
                                    "  1、SELECT DATE_PARSE('2025-06-17', '%Y-%m-%d') AS parsed_date;\n" +
                                    "    输出: DATE '2025-06-17'  \n" +
                                    "  2、SELECT DATE_PARSE('2025-06-17 14:30:45', '%Y-%m-%d %H:%i:%s') AS parsed_timestamp;\n" +
                                    "    输出: TIMESTAMP '2025-06-17 14:30:45' \n" +
                                    "- 在编写 SQL 时，在日期格式化函数中使用两个连续的百分号是错误的。例如，DATE_FORMAT(date_field, '%%Y-%%m') 是错误的。正确的格式应该使用单个百分号，例如 '%Y-%m'\n" +
                                    "- 将日期转为'月'时使用strftime(<日期字段>,'%Y-%m')，如果日期字段为字符串，则需要先转换：strftime(CAST(<日期字段> AS DATE),'%Y-%m')\n" +
                                    "- 将日期转为'日'时使用strftime(<日期字段>,'%Y-%m-%d')，如果日期字段为字符串，则需要先转换：strftime(CAST(<日期字段> AS DATE,'%Y-%m-%d'))\n" +
                                    "- 计算昨天(1天前)使用CURRENT_DATE - INTERVAL '1' day；计算前天(2天前)使用CURRENT_DATE - INTERVAL '2' day\n" +
                                    "- 计算N天前使用CURRENT_DATE - INTERVAL '<N>' day，例如计算6天前：CURRENT_DATE - INTERVAL '6' day\n" +
                                    "- 计算N天前使用CURRENT_DATE - INTERVAL '<N>' month，例如计算上个月：CURRENT_DATE - INTERVAL '1' month\n" +
                                    "- 计算N年前使用CURRENT_DATE - INTERVAL '<N>' year，例如计算上一年：CURRENT_DATE - INTERVAL '1' 年\n" +
                                    "- 表名前必须要指定catalog和schema")
                                    .name("语义SQL修正")
                                    .appModule(AppModule.CHAT)
                                    .description("通过大模型对解析S2SQL做二次修正")
                                    .enable(true)
                                    .build()
                    )
            ).collect(toMap(AbstractMap.SimpleEntry::getKey, AbstractMap.SimpleEntry::getValue));

}
