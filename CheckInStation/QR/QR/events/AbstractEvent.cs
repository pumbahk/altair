using System;
using System.Collections.Generic;
using NLog;

namespace QR
{
	public abstract class AbstractEvent
	{
		public List<string> messages;

		public virtual string GetMessageFormat ()
		{
			return "message: {0}";
		}

		public InternalEventStaus Status { get; set; }

		public AbstractEvent ()
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
				Console.WriteLine (GetMessageFormat (), m);
			}
			messages.Clear ();
		}
	}
}

