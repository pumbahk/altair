using System;
using checkin.core.models;

namespace checkin.core.message
{
    public static class UrlResourceUtil
    {
        public static string GetLoginURL (this IResource resource)
        {
            return resource.SettingValue ("endpoint.auth.login.url");
        }

        public static string GetMockLoginURL(this IResource resource)
        {
            return resource.SettingValue ("endpoint.mock.auth.login.url");
        }
        public static string GetDevelopLoginURL(this IResource resource)
        {
            return resource.SettingValue("endpoint.develop.auth.login.url");
        }
        public static string GetStagingLoginURL(this IResource resource)
        {
            return resource.SettingValue("endpoint.staging.auth.login.url");
        }
    }
}

