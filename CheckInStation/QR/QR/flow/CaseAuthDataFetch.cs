using System;
using System.Threading.Tasks;
using QR.message;
using NLog;

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

        public override async Task<bool> VerifyAsync ()
        {
            try {
                ResultTuple<string, AuthInfo> result = await Resource.Authentication.AuthAsync (LoginName, LoginPassword);
                if (result.Status) {
                    Resource.AuthInfo = result.Right;
                    return true;
                } else {
                    //modelからpresentation層へのメッセージ
                    PresentationChanel.NotifyFlushMessage ((result as Failure<string,AuthInfo>).Result);
                    return false;
                }
            } catch (Exception ex) {
                logger.ErrorException (":", ex);
                PresentationChanel.NotifyFlushMessage (MessageResourceUtil.GetTaskCancelMessage (Resource));
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
