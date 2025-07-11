package com.tencent.supersonic.common.config;

import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;

@Configuration
public class JdbcTemplateConfig {

    @Bean
    public JdbcTemplate jdbcTemplate(@Qualifier("h2") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }

    /**
     * @description: trinoJdbcTemplate
     * @param: dataSource
     * @return: JdbcTemplate
     * @throws
     * @author
     * @date 2025/5/28 15:19
     **/
    @Bean
    public JdbcTemplate trinoJdbcTemplate(@Qualifier("trino") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}
