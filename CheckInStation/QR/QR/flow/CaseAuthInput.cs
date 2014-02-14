using System;
using System.Threading.Tasks;

namespace QR
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
            return Task.Run(() => {
                var subject = this.PresentationChanel as AuthenticationEvent;
                this.LoginName = subject.LoginName;
                if (LoginName.Equals(""))
                {
                    subject.NotifyFlushMessage("名前が未入力です。入力してください");
                    return false;
                }
                return true;
            });
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

