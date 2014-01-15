using System;
using System.Threading.Tasks;

namespace QR
{
	public class FakeTicketImagePrinting :ITicketImagePrinting
	{
		public Task<bool> EnqueuePrinting (byte[] imageBytes)
		{
			return Task.Run (() => {
				Console.WriteLine ("Printing image!");
				return true;
			});
		}
	}
}