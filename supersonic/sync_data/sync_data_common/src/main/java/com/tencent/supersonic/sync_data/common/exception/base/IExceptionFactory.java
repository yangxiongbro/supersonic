package com.tencent.supersonic.sync_data.common.exception.base;

/**
 * <b><code>IBaseException</code></b>
 * <p/>
 * 创建异常接口
 * <p/>
 * <b>Creation Time:</b> 2022/8/24 上午11:53.
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public interface IExceptionFactory {
    /**
     * @description: 创建异常
     * @param args
     * @return {@link BaseException}
     * @throws
     * @author yang xiong
     * @date 2022/8/24 上午11:38
     */
    BaseException newException(Object... args);

    /**
     * @description: 创建异常
     * @param t
     * @param args
     * @return {@link BaseException}
     * @throws
     * @author yang xiong
     * @date 2022/8/24 上午11:38
     */
    BaseException newException(Throwable t, Object... args);
}
