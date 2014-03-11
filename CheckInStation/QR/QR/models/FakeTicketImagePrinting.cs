using System;
using System.Threading.Tasks;

namespace QR
{
    public class FakeTicketImagePrinting : ITicketPrinting
    {
        public Task<bool> EnqueuePrinting(TicketImageData imagedata, IInternalEvent ev)
        {
            Console.WriteLine("Printing image!: token id={0}", imagedata.token_id);
            return Task.Run(() => true);
        }
        public System.Printing.PrintQueue DefaultPrinter { get; set; }
        public System.Printing.PrintQueueCollection AvailablePrinters()
        {
            return null; // dummy/
        }
        public void BeginEnqueue(){ }
        public void EndEnqueue() { }
    }
}