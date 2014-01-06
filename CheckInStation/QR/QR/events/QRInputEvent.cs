using System;

namespace QR
{
	public class QRInputEvent : AbstractEvent, IInternalEvent
	{
		public string QRCode { get; set;}
		public QRInputEvent () :base()
		{
		}
	}
}

