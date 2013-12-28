using System;
using System.Collections.Generic;

namespace QR
{
	public class AuthenticationEvent :IInternalEvent
	{
		public string LoginName{ get; set; }

		public string LoginPassword{ get; set; }

		public string ValidationErrorMessage{ get; set; }

		private List<string> messages;

		public InternalEventStaus Status { get; set; }

		public bool NotifyFlushMessage (string message)
		{
			messages.Add (message);
			return true;
		}

		public void HandleEvent ()
		{
			foreach (var m in messages) {
				Console.WriteLine ("message: {0}", m);
			}
			messages.Clear ();
		}

		public AuthenticationEvent ()
		{
			messages = new List<string> ();
		}

		public AuthenticationEvent (string name, string password) : this()
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

