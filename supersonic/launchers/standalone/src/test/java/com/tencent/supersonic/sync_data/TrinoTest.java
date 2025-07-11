package com.tencent.supersonic.sync_data;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.sql.*;
import java.util.List;
import java.util.Properties;
import java.util.stream.Collectors;
import java.util.stream.Stream;


/**
 * <b><code>TestTrino</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/5/28 15:15
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public class TrinoTest {
    private String url = "jdbc:trino://192.168.5.189:18080";
    // private String url = "jdbc:trino://192.168.63.189:18080";

    public Properties getProperties() {
        Properties properties = new Properties();
        properties.setProperty("user", "demo");
//        properties.setProperty("password", "123456");
        return properties;
    }

    @Test
    public void createCatalog(){
        try (Connection connection = DriverManager.getConnection(url, getProperties());
            Statement statement = connection.createStatement();){
            String sql = "CREATE CATALOG \"socpg2-test\" USING postgresql\n" +
                    "WITH (\n" +
                    "  \"connection-url\" = 'jdbc:postgresql://192.168.16.97:5432/soc?currentSchema=public&useUnicode=true&characterEncoding=utf8',\n" +
                    "  \"connection-user\" = 'postgres',\n" +
                    "  \"connection-password\" = 'postgres'\n" +
                    ")";
            int rs = statement.executeUpdate(sql);
            System.out.println(rs);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    @Test
    public void dropCatalog(){
        try (Connection connection = DriverManager.getConnection(url, getProperties());
            Statement statement = connection.createStatement();){
            List<String> sqls = Stream.of(
                            "drop catalog \"dy_mysql_3\"",
                            "drop catalog \"soc_pg_2\""
                    )
                    .collect(Collectors.toList());
            for (String sql : sqls) {
                System.out.println(sql);
                int rs = statement.executeUpdate(sql);
                System.out.println(rs);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testShow(){
        try (Connection connection = DriverManager.getConnection(url, getProperties());
            Statement statement = connection.createStatement();){
            // show catalogs like '%mysql%'
            // show schemas from dy_mysql_5
            // show tables from soc_pg_3.public
            // show tables from dy_mysql_5."cmicsed-dyprdp-test"
            print(statement.executeQuery("show catalogs like 'dy_2'"));
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void print(ResultSet rs) throws SQLException {
        int columnNum = rs.getMetaData().getColumnCount();
        while (rs.next()) {
            for (int i = 1; i <= columnNum; i++) {
                System.out.print("\t");
                System.out.println(rs.getString(i));
            }
        }
    }

}
