package com.tencent.supersonic.sync_data.common.utils;

import org.springframework.util.StringUtils;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * <b><code>UrlUtils</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/14 13:28
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public class UrlUtils {

    public static Pattern ipPortPattern =
            Pattern.compile("(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):(\\d+)");

    public static String[] extractIpPort(String url) {
        String[] ipHost = new String[2];
        if (StringUtils.hasText(url)) {
            Matcher matcher = ipPortPattern.matcher(url);
            if (matcher.find()) {
                ipHost[0] = matcher.group(1);
                ipHost[1] = matcher.group(2);
            }
        }
        return ipHost;
    }
}
