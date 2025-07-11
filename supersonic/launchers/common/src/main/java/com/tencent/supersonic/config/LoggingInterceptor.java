package com.tencent.supersonic.config;

import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.util.StreamUtils;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * <b><code>LoggingInterceptor</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/16 15:30
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */

public class LoggingInterceptor implements ClientHttpRequestInterceptor {
    @Override
    public ClientHttpResponse intercept(HttpRequest request, byte[] body, ClientHttpRequestExecution execution) throws IOException {
        // 记录请求信息
        System.out.println("=== Request ===");
        System.out.println("URI: " + request.getURI());
        System.out.println("Method: " + request.getMethod());
        System.out.println("Headers: " + request.getHeaders());
        System.out.println("Body: " + new String(body, StandardCharsets.UTF_8));

        // 执行请求
        ClientHttpResponse response = execution.execute(request, body);

        // 记录响应信息
        System.out.println("=== Response ===");
        System.out.println("Status: " + response.getStatusCode());
        System.out.println("Headers: " + response.getHeaders());
        System.out.println("Body: " + StreamUtils.copyToString(response.getBody(), StandardCharsets.UTF_8));

        return response;
    }
}
