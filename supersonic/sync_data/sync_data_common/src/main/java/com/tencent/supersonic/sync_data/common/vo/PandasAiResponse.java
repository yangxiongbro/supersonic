package com.tencent.supersonic.sync_data.common.vo;

import lombok.Data;
import org.springframework.http.HttpStatus;

import java.io.Serializable;

/**
 * <b><code>PandasAiResponse</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/6/3 14:53
 *
 * @author yang xiong
 * @since supersonic 0.1.0
 */
@Data
public class PandasAiResponse<T> implements Serializable {

    private int code;

    private String msg;

    private T data;

    public static <T> PandasAiResponse<T> ok() {
        return restResult(HttpStatus.OK, null);
    }

    public static <T> PandasAiResponse<T> ok(T data) {
        return restResult(HttpStatus.OK, data);
    }

    public static <T> PandasAiResponse<T> ok(T data, String msg) {
        return restResult(HttpStatus.OK.value(), msg, data);
    }

    public static <T> PandasAiResponse<T> failed() {
        return restResult(HttpStatus.INTERNAL_SERVER_ERROR, null);
    }

    public static <T> PandasAiResponse<T> failed(String msg) {
        return restResult(HttpStatus.INTERNAL_SERVER_ERROR.value(), msg, null);
    }

    public static <T> PandasAiResponse<T> failed(HttpStatus httpStatus, String msg) {
        return restResult(httpStatus.value(), msg, null);
    }

    public static <T> PandasAiResponse<T> failed(T data) {
        return restResult(HttpStatus.INTERNAL_SERVER_ERROR, data);
    }

    public static <T> PandasAiResponse<T> failed(T data, String msg) {
        return restResult(HttpStatus.INTERNAL_SERVER_ERROR.value(), msg, data);
    }

    private static <T> PandasAiResponse<T> restResult(HttpStatus httpStatus, T data) {
        return restResult(httpStatus.value(), httpStatus.getReasonPhrase(), data);
    }

    private static <T> PandasAiResponse<T> restResult(int code, String msg, T data) {
        PandasAiResponse<T> apiResult = new PandasAiResponse<>();
        apiResult.setCode(code);
        apiResult.setMsg(msg);
        apiResult.setData(data);
        return apiResult;
    }
}
