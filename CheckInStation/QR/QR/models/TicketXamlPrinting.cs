using NLog;
using System;
using System.IO;
using System.Printing;
using System.Threading.Tasks;
using System.Windows.Documents;
using System.Windows.Media.Imaging;

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

		public bool EnqueuePrinting (TicketImageData imageData)
		{

			PrintQueue pq = this.DefaultPrinter;
			this.writer = PrintQueue.CreateXpsDocumentWriter(pq);

			var r = new StringReader(imageData.xaml);
			var xmlreader = XmlReader.Create(r);
			var doc = XamlReader.Load(xmlreader) as FixedDocument;

			//
			FixedPage.SetTop(img, 0);
			FixedPage.SetLeft(img, 0);

			writer.Write(doc); //todo: PrintTicket

			this.doc = null;
			this.writer = null;
			return true;
		}

		public PrintQueueCollection AvailablePrinters()
		{
			return this.ps.GetPrintQueues();
		}
		public void BeginEnqueue ()
		{
			throw new NotImplementedException ();
		}
		public void EndEnqueue ()
		{
			throw new NotImplementedException ();
		}
		#endregion
	}
	
}
