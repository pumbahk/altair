using System;

namespace QR
{
    public class AuthConfiguration
    {
        public static void IncludeMe(IConfigurator config)
        {
            var loginUrl = config.Resource.GetLoginURL ();
            config.Resource.Authentication = new Authentication (config.Resource, loginUrl);
        }
        public static void MockIncludeMe(IConfigurator config)
        {
            var loginUrl = config.Resource.GetMockLoginURL ();
            config.Resource.Authentication = new Authentication (config.Resource, loginUrl);
        }
    }
}

