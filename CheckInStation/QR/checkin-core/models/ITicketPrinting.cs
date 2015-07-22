using System;
using System.Printing;
using System.Threading.Tasks;
using checkin.core.events;

namespace checkin.core.models
{
    public interface ITicketPrinting
    {
        bool EnqueuePrinting (TicketImageData imageData, IInternalEvent ev);
        PrintQueueCollection AvailablePrinters();
        PrintQueue DefaultPrinter { get; set; }
        void BeginEnqueue();
        void EndEnqueue();
    }
}

