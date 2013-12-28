using System;
using System.Collections.Generic;

namespace QR
{
	public class EmptyEvent :IInternalEvent
	{
		private List<string> messages;

		public InternalEventStaus Status { get; set; }

		public EmptyEvent ()
		{
			messages = new List<string> ();
		}

		public bool NotifyFlushMessage (string message)
		{
			messages.Add (message);
			return true;
		}

		public void HandleEvent ()
		{
			foreach (var m in messages) {
				Console.WriteLine ("empty: message: {0}", m);
			}
			messages.Clear ();
		}
	}
}

