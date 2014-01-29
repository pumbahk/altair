using System;
using System.IO;
using System.Printing;
using System.Threading.Tasks;
using System.Windows.Documents;
using System.Windows.Media.Imaging;

namespace QR
{

	public class TicketImagePrinting :ITicketImagePrinting
	{
		public IResource Resource { get; set; }

        private LocalPrintServer ps;
        private System.Windows.Xps.XpsDocumentWriter writer;
        private FixedDocument doc;
        public PrintQueue DefaultPrinter { get; set; }        

        //temporary variable
		public TicketImagePrinting (IResource resource)
		{
			Resource = resource;
            this.ps = new LocalPrintServer();
            this.DefaultPrinter = this.ps.DefaultPrintQueue;
		}

        public PrintQueueCollection AvailablePrinters()
        {
            return this.ps.GetPrintQueues();
        }

		public bool EnqueuePrinting(TicketImageData imageData)
		{
            // get image
            var bmi = ImageUtil.LoadImage(imageData.image);
            var img = new System.Windows.Controls.Image() { Width = bmi.PixelWidth, Height = bmi.PixelHeight, Source = bmi };

            // build fixed document
            var pageContent = new PageContent() { Width = img.Width, Height = img.Height };
            var page = new FixedPage() { Width = img.Width, Height = img.Height };

            ///xxx:
            FixedPage.SetTop(img, 0);
            FixedPage.SetLeft(img, 0);

            //add queue
            page.Children.Add(img);
            pageContent.Child = page;
            this.doc.Pages.Add(pageContent);
            return true;
		}

        public void BeginEnqueue()
        {
            PrintQueue pq = this.DefaultPrinter;
            this.writer = PrintQueue.CreateXpsDocumentWriter(pq);
            this.doc = new FixedDocument();
        }

        public void EndEnqueue()
        {
            // printing
            writer.WriteAsync(doc); //todo: PrintTicket
            // xxx: warning not async
            this.doc = null;
            this.writer = null;
        }
	}
}

