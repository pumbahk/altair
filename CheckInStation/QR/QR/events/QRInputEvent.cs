using System;

namespace QR
{
	public enum InputUnit
	{
		qrcode = 0,
		orderno = 1
	}

	public class QRInputEvent : AbstractEvent, IInternalEvent
	{
		public string QRCode { get; set; }

		public InputUnit InputUnit { get; set; }

		public string InputUnitString { get; set; }

		public QRInputEvent () : base ()
		{
		}
	}
}

