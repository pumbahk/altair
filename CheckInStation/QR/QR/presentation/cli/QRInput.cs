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
				Console.WriteLine ("------QRCode input unit select: 1:qr, 2:orderno-----");
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
			Console.WriteLine ("-------QRCode DataFetch *ticket data*--------");
			result = await RequestBroker.Submit (ev);
			ev.HandleEvent ();

			Console.WriteLine ("--------QRCode Confirm for one print unit select: 1:one, 2:all-------------------");
			ev.PrintUnitString = Console.ReadLine ();
			result = await RequestBroker.Submit (ev);
			ev.HandleEvent ();

			Console.WriteLine ("-------QRCode DataFetch *svg data*-----");
			result = await RequestBroker.Submit (ev);
			ev.HandleEvent ();
			return result;
		}
	}
}

