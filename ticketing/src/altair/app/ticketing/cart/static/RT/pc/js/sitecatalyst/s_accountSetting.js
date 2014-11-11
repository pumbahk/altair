var accountSetting = {};

// set RSID for your environment
accountSetting.useLog = false;
accountSetting.listingParamName = "sclid";
accountSetting.campaignParamName = "scid,sclid";
accountSetting.defaultRSID = "[default RSID]";
//change bellow to false for DEV/STG environment
accountSetting.dynamicAccountSelection=false
accountSetting.dynamicAccountList="[DEV RSID]=some-domain,some-domain2;[PRD RSID]=some-domain-prd,some-domain-prd2";
accountSetting.serviceName = "[service name]";
accountSetting.cookieDomainPeriods="3"
accountSetting.currencyCode = "JPY";
accountSetting.trackDownloadLinks = false;
accountSetting.trackExternalLinks = false;
accountSetting.usePrePlugins = true;
accountSetting.usePostPlugins = true;
accountSetting._internalSite = new Array();
accountSetting._internalSite[0] = "javascript:";
accountSetting._internalSite[1] = "upc.rakuten.co.jp";
accountSetting._internalSite[2] = "auto.rakuten.co.jp";


/*** DON'T TOUCH ***/
accountSetting.linkInternalFilters = accountSetting._internalSite.join(",");