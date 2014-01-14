using System;

namespace QR
{
	public enum InputUnit
	{
		qrcode = 1,
		orderno = 2
	}

	public enum PrintUnit
	{
		one,
		all
	}

	public class QRInputEvent : AbstractEvent, IInternalEvent
	{
		public string QRCode { get; set; }

		public InputUnit InputUnit { get; set; }

		public string InputUnitString { get; set; }

		public PrintUnit PrintUnit { get; set; }

		public string PrintUnitString { get; set; }

		public bool TryParseEnum<T> (string target, out T result)
		{
			try {
				result = (T)Enum.Parse (typeof(T), target);
				return true;
			} catch (Exception e) {
				Console.WriteLine (e.ToString ());
				result = default(T);
				return false;
			}
		}

		public QRInputEvent () : base ()
		{
		}
	}
}

