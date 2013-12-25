using System;

namespace QR
{
	public class AuthenticationEvent :IInternalEvent
	{
		public string LoginName{ get; set;}
		public string LoginPassword{ get; set;}

		public AuthenticationEvent ()
		{
		}
	}
}

