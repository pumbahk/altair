using System;
using System.Threading.Tasks;

namespace QR
{
	public interface ITicketImagePrinting
	{
		Task<bool> EnqueuePrinting (byte[] imageBytes);
	}
}

