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

		public string LoginPassword { get; set; }

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
                this.LoginPassword = subject.LoginPassword;
                var status = true;
                if (LoginName.Equals(""))
                {
                    subject.NotifyFlushMessage("名前が未入力です。入力してください");
                    status = false;
                }
                if (LoginPassword.Equals(""))
                {
                    subject.NotifyFlushMessage("パスワードが未入力です。入力してください");
                    status = false;
                }
                return status;
            });
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseAuthDataFetch (Resource, LoginName, LoginPassword);
		}

		public override ICase OnFailure (IFlow flow)
		{
			return this;
		}
	}
}

