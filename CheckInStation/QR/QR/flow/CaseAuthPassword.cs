using System;
using System.Threading.Tasks;

namespace QR
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
            return Task.Run(() =>
            {
                var subject = this.PresentationChanel as AuthenticationEvent;
                this.LoginPassword = subject.LoginPassword;
                if (LoginPassword.Equals(""))
                {
                    subject.NotifyFlushMessage("パスワードが未入力です。入力してください");
                    return false;
                }
                return true;
            });
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

