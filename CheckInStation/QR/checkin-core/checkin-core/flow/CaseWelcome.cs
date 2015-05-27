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
    public class CaseWelcome : AbstractCase, ICase
    {
        public int PrintType { set; get; }
        public CaseWelcome(IResource resource)
            : base(resource)
        {
        }
        public CaseWelcome(IResource resource, int printtype)
            : base(resource)
        {
            this.PrintType = printtype;
        }
        public override async Task<bool> VerifyAsync()
        {        
            return true;
        }
        public override ICase OnSuccess (IFlow flow)
        {
            flow.Finish();
            if ((this.PresentationChanel as WelcomeEvent).PrintType == 1)
            {
                return flow.GetFlowDefinition().AfterWelcome(Resource);
            }
            else
            {
                return flow.GetFlowDefinition().AfterWelcome(Resource);
            }
           
        }

        public override ICase OnFailure(IFlow flow)
        {
            return this;
        }
    }
}
