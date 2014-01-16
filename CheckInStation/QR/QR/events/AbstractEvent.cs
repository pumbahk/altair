using System;
using System.Collections.Generic;
using NLog;

namespace QR
{
	public abstract class AbstractEvent
	{
		public List<string> messages;
		private static Logger logger = LogManager.GetCurrentClassLogger ();

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
		//todo:move
		public bool TryParseEnum<T> (string target, out T result)
		{
			try {
				result = (T)Enum.Parse (typeof(T), target);
				return true;
			} catch (ArgumentException ex) {
				logger.Error ("{0} is undefined value. default value {1} is selected.", target, default(T));
				result = default(T);
				return true;
			} catch (Exception e) {
				logger.ErrorException (":", e);
				result = default(T);
				return false;
			}
		}
	}
}

