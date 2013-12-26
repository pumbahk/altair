using System;

namespace QR
{
	public class AuthenticationEvent :IInternalEvent
	{
		public string LoginName{ get; set; }

		public string LoginPassword{ get; set; }

		public string ValidationErrorMessage{ get; set; }

		public AuthenticationEvent (string name, string password)
		{
			LoginName = name;
			LoginPassword = password;
		}

		public void AuthenticationFailure (string message)
		{
			//ここは非同期にする必要ないのかー。
			ValidationErrorMessage = message;
		}
	}
}

