using System;

namespace QR
{
	public enum InputUnit
	{
		qrcode = 0,
		order_no = 1
	}

	public class SelectInputStragetyEvent : AbstractEvent, IInternalEvent
	{
		public InputUnit InputUnit { get; set; }

		public string InputUnitString { get; set; }
	}
}

