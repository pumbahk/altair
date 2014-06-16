using System;
using System.Configuration;
using checkin.core.support;
using NLog;
using checkin.core.models;

namespace checkin.core
{
    public class Configurator : IConfigurator
    {
        public IResource Resource { get; set; }
        public ReleaseStageType ReleaseStageType { get; set; }
        public FlowDefinitionType FlowDefinitionType { get; set; }
        public static Logger logger = LogManager.GetCurrentClassLogger();

        public Configurator (IResource resource)
        {
            Resource = resource;
            this.ReleaseStageType = (ReleaseStageType)Enum.Parse(typeof(ReleaseStageType), resource.SettingValue("application.stage"));
            this.FlowDefinitionType = (FlowDefinitionType)Enum.Parse(typeof(FlowDefinitionType), resource.SettingValue("application.flow"));
            logger.Info("application.stage = {0}".WithMachineName(), this.ReleaseStageType);
            logger.Info("application.flow = {0}".WithMachineName(), this.FlowDefinitionType);
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

