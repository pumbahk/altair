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
        public CaseWelcome(IResource resource)
            : base(resource)
        {
        }
        public override async Task<bool> VerifyAsync()
        {
            //var ts = new TaskCompletionSource<bool>();
            //return ts.Task;
            //var d = new DispatchResponse<AuthInfo>(this.Resource);
            //ResultTuple<string, AuthInfo> result = await d.Dispatch(() => Resource.Authentication.AuthAsync(LoginName, LoginPassword)).ConfigureAwait(false);
            
            return true;
        }
        public override ICase OnSuccess (IFlow flow)
        {
            flow.Finish();
            return flow.GetFlowDefinition().AfterWelcome(Resource);
        }

        public override ICase OnFailure(IFlow flow)
        {
            return this;
        }
    }
}
