package com.tencent.supersonic.sync_data.common.config;

import com.tencent.supersonic.headless.core.pojo.ConnectInfo;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * <b><code>TrinoConfig</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/5/28 17:22
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */

@Configuration
public class TrinoConfig {

    @Bean
    @ConfigurationProperties("spring.datasource-trino")
    public ConnectInfo trinoConnectInfo(){
        DataSourceProperties properties = new DataSourceProperties();
        ConnectInfo connectInfo = new ConnectInfo();
        connectInfo.setUserName(properties.getUsername());
        connectInfo.setPassword(properties.getPassword());
        connectInfo.setUrl(properties.getUrl());
//        connectInfo.setDatabase(database.getDatabase());
        return connectInfo;
    }
}
