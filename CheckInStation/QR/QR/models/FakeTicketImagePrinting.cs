using System;
using System.Threading.Tasks;

namespace QR
{
    public class FakeTicketImagePrinting : ITicketImagePrinting
    {
        public bool EnqueuePrinting(TicketImageData imagedata)
        {
            Console.WriteLine("Printing image!: token id={0}", imagedata.token_id);
            return true;
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