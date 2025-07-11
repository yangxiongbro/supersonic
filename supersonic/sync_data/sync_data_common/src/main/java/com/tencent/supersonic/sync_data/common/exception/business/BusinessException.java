package com.tencent.supersonic.sync_data.common.exception.business;

import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.exception.base.IExceptionAssertResponseEnum;

/**
 * <b><code>BusinessException</code></b>
 * <p/>
 * 业务异常
 * <p/>
 * <b>Creation Time:</b> 2022/8/24 下午12:34.
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public class BusinessException extends BaseException {

    private static final long serialVersionUID = 1L;

    public BusinessException(IExceptionAssertResponseEnum exceptionAssertResponseEnum, Object[] args, String message) {
        super(exceptionAssertResponseEnum, args, message);
    }

    public BusinessException(IExceptionAssertResponseEnum exceptionAssertResponseEnum, Object[] args, String message, Throwable cause) {
        super(exceptionAssertResponseEnum, args, message, cause);
    }
}
