using System;
using System.Printing;
using System.Threading.Tasks;

namespace QR
{
	public interface ITicketImagePrinting
	{
		bool EnqueuePrinting (TicketImageData imageData);
        PrintQueueCollection AvailablePrinters();
        PrintQueue DefaultPrinter { get; set; }
        void BeginEnqueue();
        void EndEnqueue();
	}
}

