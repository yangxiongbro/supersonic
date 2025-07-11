package com.tencent.supersonic.sync_data.common.exception.business;

import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import com.tencent.supersonic.sync_data.common.exception.base.IExceptionAssertResponseEnum;

import java.text.MessageFormat;

/**
 * <b><code>AbstractBusinessExceptionAssert</code></b>
 * <p/>
 * 创建异常接口实现类，由于枚举不能继承，所以不能使用抽象类
 * <p/>
 * <b>Creation Time:</b> 2022/8/24 下午12:09.
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
public interface BaseBusinessExceptionFactory extends IExceptionAssertResponseEnum, BaseBusinessAssert {
    @Override
    default BaseException newException(Object... args) {
        String msg = MessageFormat.format(this.getMessage(), args);

        return new BusinessException(this, args, msg);
    }

    @Override
    default BaseException newException(Throwable t, Object... args) {
        String msg = MessageFormat.format(this.getMessage(), args);

        return new BusinessException(this, args, msg, t);
    }
}
