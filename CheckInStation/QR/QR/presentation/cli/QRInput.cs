using System;

namespace QR.presentation.cli
{
	public class QRInput
	{
		public RequestBroker RequestBroker { get; set; }

		public ICase Case { get; set; }

		public QRInput (RequestBroker broker, ICase case_)
		{
			RequestBroker = broker;
			Case = case_;			
		}

		public ICase Run ()
		{
			ICase result;
			var ev = new QRInputEvent ();
			do {
				do {
					Console.WriteLine ("------QRCode input---------");
					Console.Write ("qrcode:");
					ev.QRCode = Console.ReadLine ();
					result = RequestBroker.Submit (ev);
					ev.HandleEvent ();
				} while(ev.Status == InternalEventStaus.failure);
				result = RequestBroker.Submit(ev);
				ev.HandleEvent();
			} while(ev.Status == InternalEventStaus.failure);
			return result;
		}
	}
}

