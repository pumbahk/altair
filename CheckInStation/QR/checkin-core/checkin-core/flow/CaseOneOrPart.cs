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
    public class CaseOneOrPart : AbstractCase, ICase
    {
        public int PrintCount { set; get; }
        public TicketData Tdata { set; get; }
        public CaseOneOrPart(IResource resource)
            : base(resource)
        {
        }
        public CaseOneOrPart(IResource resource, int printcount)
            : base(resource)
        {
            this.PrintCount = printcount;
        }
        public CaseOneOrPart(IResource resource, TicketData tdata)
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
            //flow.Finish();
            return flow.GetFlowDefinition().AfterCountChoice(Resource, (this.PresentationChanel as OneOrPartEvent).PrintCount, this.Tdata);

        }

        public override ICase OnFailure(IFlow flow)
        {
            return this;
        }
    }
}
