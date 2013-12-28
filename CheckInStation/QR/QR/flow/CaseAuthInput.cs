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

		public override void Configure (IInternalEvent ev)
		{
			AuthenticationEvent subject = ev as AuthenticationEvent;
			this.LoginName = subject.LoginName;
			this.LoginPassword = subject.LoginPassword;
			base.Configure (ev);
		}

		public override bool Verify ()
		{
			return !LoginName.Equals ("") && !LoginPassword.Equals ("");
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseAuthDataFetch (Resource, LoginName, LoginPassword);
		}

		public override ICase OnFailure (IFlow flow)
		{
			PresentationChanel.NotifyFlushMessage ("login failure");
			return this;
		}
	}
}

