using System;
using System.Threading.Tasks;
using System.Collections.Generic;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case QR print finish. 発券しました
    /// </summary>
    public class CasePrintFinish: AbstractCase,ICase,IAutoForwardingCase
    {
        public UpdatePrintedAtRequestData RequsetData { get; set; }

        public CasePrintFinish (IResource resource, UpdatePrintedAtRequestData data) : base (resource)
        {
            this.RequsetData = data;
        }

        public override async Task<bool> VerifyAsync ()
        {
            (this.PresentationChanel as FinishEvent).ChangeState(FinishStatus.requesting);
            var result = await new DispatchResponse<bool>(Resource).Dispatch(() => Resource.TicketDataManager.UpdatePrintedAtAsync (this.RequsetData)).ConfigureAwait(false);
            (this.PresentationChanel as FinishEvent).ChangeState(FinishStatus.saved);
            if (!result.Status)
            {
                this.PresentationChanel.NotifyFlushMessage(result.Left);
                return false;
            }
            return true;
        }

        public override ICase OnSuccess (IFlow flow)
        {
            flow.Finish ();
            return flow.GetFlowDefinition ().AfterPrintFinish (Resource);
        }
    }
}

