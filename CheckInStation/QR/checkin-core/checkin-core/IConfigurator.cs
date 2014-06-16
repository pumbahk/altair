using System;
using checkin.core.models;

namespace checkin.core
{
    public interface IConfigurator
    {
        void Include (Action<IConfigurator> c);
        ReleaseStageType ReleaseStageType { get; set; }
        FlowDefinitionType FlowDefinitionType { get; set; }
        IResource Resource { get; set; }
    }
}

