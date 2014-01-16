using System;
using NLog;

namespace QR
{
	public enum PrintUnit
	{
		one = 0,
		all = 1
	}

	public class QRInputEvent : AbstractEvent, IInternalEvent
	{
		public string QRCode { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public PrintUnit PrintUnit { get; set; }

		public string PrintUnitString { get; set; }

		public QRInputEvent () : base ()
		{
		}
	}
}

