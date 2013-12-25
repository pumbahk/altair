using System;

namespace QR
{
	/// <summary>
	/// Case auth input. 認証画面
	/// </summary>
	public class CaseAuthInput : AbstractCase,ICase
	{
		public string LoginName { get; set; }

		public string LoginPassword { get; set; }

		public CaseAuthInput (IResource resource) : base(resource)
		{
		}

		public override void Configure (IInternalEvent ev)
		{
			AuthenticationEvent subject = ev as AuthenticationEvent;
			this.LoginName = subject.LoginName;
			this.LoginPassword = subject.LoginPassword;
		}

		public override bool Verify (){
			try{
				var authInfo = Resource.Authentication.auth(Resource, LoginName, LoginPassword);
				Resource.AuthInfo = authInfo;
				return true;
			} catch(Exception){
				//TODO:logging message
				return false;
			}
		}

		public override ICase OnSuccess (IFlow flow)
		{
			return new CaseQRPrintForAll (Resource);
		}
	}
}

