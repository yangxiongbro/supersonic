package com.tencent.supersonic.headless.api.pojo.request;

import com.tencent.supersonic.headless.api.pojo.DataSetDetail;
import com.tencent.supersonic.headless.api.pojo.QueryConfig;
import com.tencent.supersonic.headless.api.pojo.SchemaItem;
import lombok.Data;

import java.util.List;

@Data
public class DataSetReq extends SchemaItem {

    private Long domainId;

    private DataSetDetail dataSetDetail = new DataSetDetail();

    private String alias;

    private QueryConfig queryConfig = new QueryConfig();

    private List<String> admins;

    private List<String> adminOrgs;

    public String getAdmin() {
        if (admins == null) {
            return null;
        }
        return String.join(",", admins);
    }

    public String getAdminOrg() {
        if (adminOrgs == null) {
            return null;
        }
        return String.join(",", adminOrgs);
    }
}
