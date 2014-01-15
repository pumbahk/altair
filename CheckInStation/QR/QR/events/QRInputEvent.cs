using System;
using NLog;

namespace QR
{
	public enum InputUnit
	{
		qrcode = 0,
		order_no = 1
	}

	public enum PrintUnit
	{
		one = 0,
		all = 1
	}

	public class QRInputEvent : AbstractEvent, IInternalEvent
	{
		public string QRCode { get; set; }

		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public InputUnit InputUnit { get; set; }

		public string InputUnitString { get; set; }

		public PrintUnit PrintUnit { get; set; }

		public string PrintUnitString { get; set; }

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

		public QRInputEvent () : base ()
		{
		}
	}
}

