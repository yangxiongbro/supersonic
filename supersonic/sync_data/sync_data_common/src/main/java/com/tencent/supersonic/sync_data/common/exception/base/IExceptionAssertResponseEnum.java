package com.tencent.supersonic.sync_data.common.exception.base;

/**
 * <b><code>IResponseEnum</code></b>
 * <p/>
 * 响应枚举值接口
 * <p/>
 * <b>Creation Time:</b> 2022/8/24 下午12:05.
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public interface IExceptionAssertResponseEnum {
    int getCode();
    String getMessage();
}
