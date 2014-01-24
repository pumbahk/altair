using System;

namespace QR
{
	/// <summary>
	/// I internal event. the Event from presentation layer;
	/// </summary>
	public interface IInternalEvent
	{
		void HandleEvent ();
        void HandleEvent (Action<string> useAction);
		bool NotifyFlushMessage (string message);

		InternalEventStaus Status { get; set; }
	}

	public enum InternalEventStaus
	{
		failure,
        success,
	}
}

