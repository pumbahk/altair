using System;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// Case auth input. 認証画面
    /// </summary>
    public class CaseAuthInput : AbstractCase,ICase
    {
        public string LoginName { get; set; }
        public string LoginPassword {get;set;}

        public CaseAuthInput (IResource resource) : base (resource)
        {
        }

        public CaseAuthInput (IResource resource, string name, string password) : base (resource)
        {
            this.LoginName = name;
            this.LoginPassword = password;
        }

        public override Task<bool> VerifyAsync ()
        {
            var ts = new TaskCompletionSource<bool>();
            var subject = this.PresentationChanel as AuthenticationEvent;
            this.LoginName = subject.LoginName;
            var r = this.Resource.Validation.ValidateAuthLoginName(this.LoginName);
            ts.SetResult(r.Status);
            if (!r.Status)
            {
                subject.NotifyFlushMessage(r.Left);
            }
            return ts.Task;
        }

        public override ICase OnSuccess (IFlow flow)
        {
            return new CaseAuthPassword(Resource, LoginName);
        }

        public override ICase OnFailure (IFlow flow)
        {
            return this;
        }
    }
}

