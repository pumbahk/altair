using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using checkin.core.support;
using checkin.core.flow;
using checkin.core;
using checkin.core.events;
using checkin.core.models;
using checkin.core.message;
using NLog;

namespace checkin.core.flow
{
    public class CasePartOrAll : AbstractCase, ICase
    {
        public int PrintCount { set; get; }
        public TicketData Tdata { set; get; }
        public CasePartOrAll(IResource resource)
            : base(resource)
        {
        }
        public CasePartOrAll(IResource resource, int printcount)
            : base(resource)
        {
            this.PrintCount = printcount;
        }
        public CasePartOrAll(IResource resource, TicketData tdata)
            : base(resource)
        {
            this.Tdata = tdata;
        }
        public override async Task<bool> VerifyAsync()
        {
            return true;
        }
        public override ICase OnSuccess(IFlow flow)
        {
            flow.Finish();
            return flow.GetFlowDefinition().AfterTicketChoice(Resource, (this.PresentationChanel as PartOrAllEvent).PrintCount, this.Tdata);

        }

        public override ICase OnFailure(IFlow flow)
        {
            return this;
        }
    }
}
