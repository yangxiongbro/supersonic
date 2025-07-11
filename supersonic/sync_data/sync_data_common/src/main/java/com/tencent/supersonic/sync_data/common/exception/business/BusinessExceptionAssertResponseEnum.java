package com.tencent.supersonic.sync_data.common.exception.business;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * <b><code>BusinessExceptionAssertResponseEnum</code></b>
 * <p/>
 * 业务异常断言响应枚举
 * <p/>
 * <b>Creation Time:</b> 2022/8/24 下午12:19.
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Getter
@AllArgsConstructor
public enum BusinessExceptionAssertResponseEnum implements BaseBusinessExceptionFactory {

    THROW_EXCEPTION(1000, "{0}"),

    SYNC_DATA_SOURCES_2_TRINO_FAIL(1010, "同步数据源{0}到trino失败"),

    DROP_CATALOG_FAIL(1011, "删除trino catalog({0})失败");

    /**
     * 返回码
     */
    private int code;

    /**
     * 返回消息
     */
    private String message;
}
