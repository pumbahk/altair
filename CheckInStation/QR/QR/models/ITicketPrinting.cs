using System;
using System.Printing;
using System.Threading.Tasks;

namespace QR
{
    public interface ITicketPrinting
    {
        Task<bool> EnqueuePrinting (TicketImageData imageData, IInternalEvent ev);
        PrintQueueCollection AvailablePrinters();
        PrintQueue DefaultPrinter { get; set; }
        void BeginEnqueue();
        void EndEnqueue();
    }
}

