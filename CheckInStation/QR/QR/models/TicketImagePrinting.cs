using System;
using System.Threading.Tasks;

namespace QR
{
	public class TicketImagePrinting :ITicketImagePrinting
	{
		public IResource Resource { get; set; }

		public TicketImagePrinting (IResource resource)
		{
			Resource = resource;
		}

		public Task<bool> EnqueuePrinting(TicketImageData imageData)
		{
			return Task.Run (() => {
				Console.WriteLine("Printing image!");
				return true;
			});
		}
	}
}

