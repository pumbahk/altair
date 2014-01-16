using System;
using System.Threading.Tasks;

namespace QR
{
	public class FakeTicketImagePrinting :ITicketImagePrinting
	{
		public Task<bool> EnqueuePrinting (TicketImageData imagedata)
		{
			return Task.Run (() => {
				Console.WriteLine ("Printing image!: token id={0}", imagedata.token_id);
				return true;
			});
		}
	}
}