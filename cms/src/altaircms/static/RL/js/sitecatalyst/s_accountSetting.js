var accountSetting = {};

// set RSID for your environment
accountSetting.useLog = false;
accountSetting.listingParamName = "sclid";
accountSetting.campaignParamName = "scid,sclid";
accountSetting.defaultRSID = "rakutenticketdev2";
//change bellow to false for DEV/STG environment
accountSetting.dynamicAccountSelection=true
accountSetting.dynamicAccountList="rakutenticketprod=ticket.rakuten.co.jp,rt.tstar.jp,eagles.tstar.jp,vissel.tstar.jp,tstar.jp";
accountSetting.serviceName = "ticket";
accountSetting.cookieDomainPeriods="3"
accountSetting.currencyCode = "JPY";
accountSetting.trackDownloadLinks = false;
accountSetting.trackExternalLinks = false;
accountSetting.usePrePlugins = true;
accountSetting.usePostPlugins = true;
accountSetting._internalSite = new Array();
accountSetting._internalSite[0] = "javascript:";
accountSetting._internalSite[1] = "ticket.rakuten.co.jp";
accountSetting._internalSite[2] = "rt.tstar.jp";
accountSetting._internalSite[3] = "eagles.tstar.jp";
accountSetting._internalSite[4] = "vissel.tstar.jp";
accountSetting._internalSite[5] = "tstar.jp";

/*** DON'T TOUCH ***/
accountSetting.linkInternalFilters = accountSetting._internalSite.join(",");