using NLog;
using System;
using System.IO;
using System.Printing;
using System.Threading.Tasks;
using System.Windows.Documents;
using System.Windows.Markup;
using System.Windows.Media.Imaging;
using System.Xml;

namespace QR
   {
	public class TicketXamlPrinting :ITicketPrinting
	{
		public IResource Resource { get; set; }

		private LocalPrintServer ps;
		private System.Windows.Xps.XpsDocumentWriter writer;
		private FixedDocument doc;

		private Logger logger = LogManager.GetCurrentClassLogger();

		//temporary variable
		public TicketXamlPrinting (IResource resource)
		{
			Resource = resource;
			this.ps = new LocalPrintServer();
			this.DefaultPrinter = this.ps.DefaultPrintQueue;
		}

		#region ITicketPrinting implementation
		public PrintQueue DefaultPrinter { get; set; }

		public async Task<bool> EnqueuePrinting (TicketImageData imageData, IInternalEvent ev)
		{

			PrintQueue pq = this.DefaultPrinter;
			this.writer = PrintQueue.CreateXpsDocumentWriter(pq);

			var r = new StringReader(imageData.xaml);
			var xmlreader = XmlReader.Create(r);

            //xaml‚ðobject‰»‚·‚é‚Ì‚Íui thread ‚Ì‚Ý
            FixedDocument doc = await ev.CurrentDispatcher.InvokeAsync<FixedDocument>(() =>
            {
                return XamlReader.Load(xmlreader) as FixedDocument;
            });
            
			writer.Write(doc); //todo: PrintTicket
			return true;
		}

		public PrintQueueCollection AvailablePrinters()
		{
			return this.ps.GetPrintQueues();
		}
		public void BeginEnqueue ()
		{
            //
		}
		public void EndEnqueue ()
		{
            this.doc = null;
            this.writer = null;
		}
		#endregion
	}
	
}
