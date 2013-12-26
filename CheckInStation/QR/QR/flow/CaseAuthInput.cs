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

		public AuthenticationEvent PresentationChanel { get; set; }

		public CaseAuthInput (IResource resource) : base (resource)
		{
		}

		public override void Configure (IInternalEvent ev)
		{
			AuthenticationEvent subject = ev as AuthenticationEvent;
			this.LoginName = subject.LoginName;
			this.LoginPassword = subject.LoginPassword;
			PresentationChanel = subject;
		}

		public override bool Verify ()
		{
			Task<ResultTuple<string, AuthInfo>> t = Resource.Authentication.authAsync (Resource, LoginName, LoginPassword);
			t.Wait (); //TODO:xxxx:
			if (t.Result.Status) {
				Resource.AuthInfo = t.Result.Right;
				return true;
			} else {
				//modelからpresentation層へのメッセージ
				NotifyValidationFailure (t.Result as Failure<string ,AuthInfo>);
				return false;
			}
		}

		public void NotifyValidationFailure (Failure<string, AuthInfo> failure)
		{
			if (PresentationChanel == null) {
				//TODO:logなりメッセージ
			} else {
				PresentationChanel.AuthenticationFailure (failure.Result);
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseAuthDataFetch (Resource);
		}
	}
}

