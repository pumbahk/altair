using System;
using System.Threading.Tasks;

namespace QR
{
	public class TicketImagePrinting
	{
		public IResource Resource { get; set; }

		public TicketImagePrinting (IResource resource)
		{
			Resource = resource;
		}

		public Task<bool> EnqueuePrinting(byte[] imageBytes)
		{
			return Task.Run (() => {
				Console.WriteLine("Printing image!");
				return true;
			});
		}
	}
}

