using System;

namespace QR.presentation.cli
{
	public class AuthInput
	{
		public RequestBroker RequestBroker { get; set; }
		public ICase Case { get; set; }

		public AuthInput (RequestBroker broker, ICase case_)
		{
			RequestBroker = broker;
			Case = case_;			
		}

		public ICase Run ()
		{
			ICase result;
			var ev = new AuthenticationEvent ();
			do {
				do {
					Console.WriteLine ("------login input---------");
					Console.Write ("name:");
					ev.LoginName = Console.ReadLine ();
					Console.Write ("password:");
					ev.LoginPassword = Console.ReadLine ();
					RequestBroker.Submit (ev);
					ev.HandleEvent ();
				} while(ev.Status == InternalEventStaus.failure);

				// requestn
				Console.WriteLine ("------login request---------");
				result = RequestBroker.Submit (ev);
				ev.HandleEvent ();
			} while(ev.Status == InternalEventStaus.failure);
			return result;
		}
	}
}

