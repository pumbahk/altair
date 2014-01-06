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
				var ok = false;
				do {
					try {
						Console.WriteLine ("------QRCode input strategy select: 1:qr, 2:orderno-----");
						var inputUnit = Enum.Parse (typeof(InputUnit), Console.ReadLine ());
						ok = true;
					} catch (Exception e) {
						Console.WriteLine (e.ToString ());
					}
				} while(!ok);

				do {
					Console.WriteLine ("------QRCode input---------");
					Console.Write ("qrcode:");
					ev.QRCode = Console.ReadLine ();
					result = await RequestBroker.Submit (ev);
					ev.HandleEvent ();
				} while(ev.Status == InternalEventStaus.failure);
				result = await RequestBroker.Submit (ev);
				ev.HandleEvent ();
			} while(ev.Status == InternalEventStaus.failure);
			return result;
		}
	}
}

