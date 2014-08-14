using System;
using System.Threading.Tasks;

namespace checkin.core.flow
{
    public interface IFlow
    {
        FlowManager Manager { get; }
        Task<IFlow> Forward ();
        //TODO:implement
        Task<IFlow> Backward ();

        Task PrepareAsync();
        Task<bool> VerifyAsync();

        void Finish ();

        ICase Case { get; set; }

        IFlowDefinition GetFlowDefinition ();

        bool IsAutoForwarding ();
    }
}

