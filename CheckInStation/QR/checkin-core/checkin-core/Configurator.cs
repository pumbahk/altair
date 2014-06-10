using System;
using System.Configuration;
using QR.support;
using NLog;

namespace QR
{
    public class Configurator : IConfigurator
    {
        public IResource Resource { get; set; }
        public ReleaseStageType ReleaseStageType { get; set; }
        public static Logger logger = LogManager.GetCurrentClassLogger();

        public Configurator (IResource resource)
        {
            Resource = resource;
            this.ReleaseStageType = (ReleaseStageType)Enum.Parse(typeof(ReleaseStageType), resource.SettingValue("application.stage"));
            logger.Info("application.stage = {0}".WithMachineName(), this.ReleaseStageType);
        }

        public bool Verify()
        {
            if (Resource == null) {
                throw new InvalidOperationException ("Configurator.Resource is null");
            }
            return Resource.Verify ();
        }
        public void Include (Action<IConfigurator> includeFunction)
        {
            includeFunction (this);
        }

        public string AppSettingValue (String key)
        {
            return Resource.SettingValue (key);
        }
    }
}

