using System;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case auth input. 認証画面(password)
    /// </summary>
    public class CaseAuthPassword : AbstractCase, ICase, IAutoForwardingCase
    {
        public string LoginName { get; set; }

        public string LoginPassword { get; set; }

        public CaseAuthPassword(IResource resource, string name)
            : base(resource)
        {
            this.LoginName = name;
        }

        public CaseAuthPassword(IResource resource, string name, string password)
            : base(resource)
        {
            this.LoginName = name;
            this.LoginPassword = password;
        }

        public override Task<bool> VerifyAsync()
        {
            var ts = new TaskCompletionSource<bool>();
            var subject = this.PresentationChanel as AuthenticationEvent;
            this.LoginPassword = subject.LoginPassword;
            var r = this.Resource.Validation.ValidateAuthPassword(this.LoginPassword);
            ts.SetResult(r.Status);
            if (!r.Status)
            {
                subject.NotifyFlushMessage(r.Left);
            }
            return ts.Task;
        }

        public override ICase OnSuccess(IFlow flow)
        {
            return new CaseAuthDataFetch(Resource, LoginName, LoginPassword);
        }

        public override ICase OnFailure(IFlow flow)
        {
            return this;
        }
    }
}

