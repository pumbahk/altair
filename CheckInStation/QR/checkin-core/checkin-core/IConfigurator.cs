using System;

namespace QR
{
    public interface IConfigurator
    {
        void Include (Action<IConfigurator> c);
        ReleaseStageType ReleaseStageType { get; set; }
        IResource Resource { get; set; }
    }
}

