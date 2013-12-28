using System;

namespace QR
{
	/// <summary>
	/// I internal event. the Event from presentation layer;
	/// </summary>
	public interface IInternalEvent
	{
		void HandleEvent();
		bool NotifyFlushMessage(string message);
		InternalEventStaus Status { get; set;}
	}

	public enum InternalEventStaus {
		success,
		failure
	}
}

