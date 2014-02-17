using System;
using System.Threading.Tasks;
using QR.message;
using NLog;
using QR.support;

namespace QR
{
    /// <summary>
    /// Case Auth data fetch. Authデータ取得中
    /// </summary>
    public class CaseAuthDataFetch : AbstractCase, ICase, IAutoForwardingCase
    {
        public string LoginName { get; set; }

        public string LoginPassword { get; set; }

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
                PresentationChanel.NotifyFlushMessage((result as Failure<string, AuthInfo>).Result);
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
            flow.Finish ();
            return new CaseAuthInput (Resource, this.LoginName, this.LoginPassword);
        }
    }
}
