using System;
using checkin.core;
using checkin.core.auth;
using checkin.core.message;

namespace checkin.config
{
    public class AuthConfiguration
    {
        public static void IncludeMe(IConfigurator config)
        {
            string loginURL;
            switch (config.ReleaseStageType)
            {
                case ReleaseStageType.mock:
                    loginURL = config.Resource.GetMockLoginURL();
                    break;
                case ReleaseStageType.develop:
                    loginURL = config.Resource.GetDevelopLoginURL();
                    break;
                case ReleaseStageType.staging:
                    loginURL = config.Resource.GetStagingLoginURL();
                    break;
                case ReleaseStageType.production:
                    loginURL = config.Resource.GetLoginURL();
                    break;
                default:
                    throw new InvalidOperationException("undefined release stage type");
            }
            config.Resource.Authentication = new Authentication (config.Resource, loginURL);
        }
    }
}

