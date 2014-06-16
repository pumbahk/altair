using System;
using System.Threading.Tasks;
using checkin.core.message;
using NLog;
using checkin.core.support;
using checkin.core.flow;
using checkin.core.models;

namespace checkin.core.flow
{
    /// <summary>
    /// Case Auth data fetch. Authデータ取得中
    /// </summary>
    public class CaseAuthDataFetch : AbstractCase, ICase, IAutoForwardingCase
    {
        public string LoginName { get; set; }

        public string LoginPassword { get; set; }
        public AggregateShorthandError TreatShorthandError { get; set; }
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public CaseAuthDataFetch (IResource resource, string name, string password) : base (resource)
        {
            LoginName = name;
            LoginPassword = password;
        }

        public override async Task<bool> VerifyAsync()
        {
            var d = new DispatchResponse<AuthInfo>(this.Resource);
            ResultTuple<string, AuthInfo> result = await d.Dispatch(() => Resource.Authentication.AuthAsync(LoginName, LoginPassword)).ConfigureAwait(false);
            if (result.Status)
            {
                Resource.AuthInfo = result.Right;
                return true;
            }
            else
            {
                //modelからpresentation層へのメッセージ
                this.TreatShorthandError = new AggregateShorthandError(this.PresentationChanel);
                this.TreatShorthandError.Parse(result.Left);
                return false;
            }
        }

        public override ICase OnSuccess (IFlow flow)
        {
            flow.Finish ();
            return flow.GetFlowDefinition ().AfterAuthorization (Resource);
        }

        public override ICase OnFailure (IFlow flow)
        {
            if (this.TreatShorthandError != null)
            {
                return this.TreatShorthandError.Redirect(flow);
            }
            flow.Finish ();
            return new CaseAuthInput (Resource, this.LoginName, this.LoginPassword);
        }
    }
}
