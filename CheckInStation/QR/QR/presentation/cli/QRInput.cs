using System;
using System.Threading.Tasks;

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

		public async Task<ICase> Run ()
		{
			ICase result;
			var ev = new QRInputEvent ();
			do {		
				Console.WriteLine ("------QRCode input strategy select: 1:qr, 2:orderno-----");
				ev.InputUnitString = Console.ReadLine ();
				result = await RequestBroker.Submit (ev);
				ev.HandleEvent ();
			} while(ev.Status == InternalEventStaus.failure);
			do {
				Console.WriteLine ("------QRCode input---------");
				Console.Write ("qrcode:");
				ev.QRCode = Console.ReadLine ();
				result = await RequestBroker.Submit (ev);
				ev.HandleEvent ();
			} while(ev.Status == InternalEventStaus.failure);
			Console.WriteLine ("-------QRCode DataFetch--------");
			result = await RequestBroker.Submit (ev);
			ev.HandleEvent ();

			return result;
		}
	}
}

