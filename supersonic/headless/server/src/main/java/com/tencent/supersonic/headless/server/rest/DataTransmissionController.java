package com.tencent.supersonic.headless.server.rest;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tencent.supersonic.headless.server.dto.DataTransmissionDTO;
import com.tencent.supersonic.headless.server.pojo.DataTransmissionExportParameter;
import com.tencent.supersonic.headless.server.pojo.DataTransmissionImportParameter;
import com.tencent.supersonic.headless.server.service.DataTransmissionService;
import com.tencent.supersonic.sync_data.common.exception.base.BaseException;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * <b><code>DataTransmissionController</code></b>
 * <p/>
 * <p>
 * <p/>
 * <b>Creation Time:</b> 2025/7/4 14:44
 *
 * @author yang xiong
 * @since chatdata-be 0.1.0
 */
@RestController
@RequestMapping("/api/sync_data/transmission")
public class DataTransmissionController {

    @Autowired
    private DataTransmissionService dataTransmissionService;

    @Autowired
    private ObjectMapper objectMapper;

    @GetMapping("/export")
    public DataTransmissionDTO exportData(@Valid DataTransmissionExportParameter parameter) {
        return dataTransmissionService.exportData(parameter.getDomainId(), parameter.getDataSetIdList());
    }

    @GetMapping("/export/file")
    public void exportData(HttpServletResponse response, @Valid DataTransmissionExportParameter parameter) throws IOException {
        String result = objectMapper.writeValueAsString(dataTransmissionService.exportData(parameter.getDomainId(), parameter.getDataSetIdList()));
        response.setContentType(MediaType.APPLICATION_OCTET_STREAM_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.setHeader(HttpHeaders.CONTENT_DISPOSITION, "attachment; fileName=datasets-" + System.currentTimeMillis() + ".json");
        try (OutputStreamWriter writer = new OutputStreamWriter(response.getOutputStream(), StandardCharsets.UTF_8)){
            writer.write(result);
        }
    }

    @PostMapping("/import")
    public Boolean importData(@Valid DataTransmissionImportParameter parameter) throws BaseException, IOException {
        return dataTransmissionService.importData(parameter.getDomainId(), parameter.getDatabaseId(), objectMapper.readValue(parameter.getData().getBytes(), DataTransmissionDTO.class));
    }

}
