package com.tencent.supersonic.headless.server.rest;

import com.tencent.supersonic.auth.api.authentication.utils.UserHolder;
import com.tencent.supersonic.common.pojo.User;
import com.tencent.supersonic.headless.server.persistence.dataobject.CollectDO;
import com.tencent.supersonic.headless.server.service.CollectService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** * 创建收藏指标的逻辑 */
@RestController
@RequestMapping("/api/semantic/collect")
public class CollectController {

    private CollectService collectService;

    public CollectController(CollectService collectService) {
        this.collectService = collectService;
    }

    @PostMapping("/createCollectionIndicators")
    public boolean createCollectionIndicators(@RequestBody CollectDO collectDO,
            HttpServletRequest request, HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return collectService.collect(user, collectDO);
    }

    @Deprecated
    @DeleteMapping("/deleteCollectionIndicators/{id}")
    public boolean deleteCollectionIndicators(@PathVariable Long id, HttpServletRequest request,
            HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return collectService.unCollect(user, id);
    }

    @PostMapping("/deleteCollectionIndicators")
    public boolean deleteCollectionIndicators(@RequestBody CollectDO collectDO,
            HttpServletRequest request, HttpServletResponse response) {
        User user = UserHolder.findUser(request, response);
        return collectService.unCollect(user, collectDO);
    }
}
