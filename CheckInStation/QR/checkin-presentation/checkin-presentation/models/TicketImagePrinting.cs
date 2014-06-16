using NLog;
using System;
using System.IO;
using System.Printing;
using System.Threading.Tasks;
using System.Windows.Documents;
using System.Windows.Media.Imaging;
using checkin.core.support;
using checkin.core.models;
using checkin.core.events;

namespace checkin.presentation.models
   {
    public class TicketImagePrinting : ITicketPrinting
    {
        public IResource Resource { get; set; }

        private LocalPrintServer ps;
        private System.Windows.Xps.XpsDocumentWriter writer;
        private FixedDocument doc;
        public PrintQueue DefaultPrinter { get; set; }


        private Logger logger = LogManager.GetCurrentClassLogger();

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

        public bool EnqueuePrinting(TicketImageData imageData, IInternalEvent ev)
        {
            PrintQueue pq = this.DefaultPrinter;
            this.writer = PrintQueue.CreateXpsDocumentWriter(pq);
            this.doc = new FixedDocument();

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
            writer.Write(doc); //todo: PrintTicket

            this.doc = null;
            this.writer = null;
            return true;
        }
        

        public void BeginEnqueue()
        {
            logger.Info("Printer: {0}".WithMachineName(), this.DefaultPrinter.FullName);
        }

        public void EndEnqueue()
        {
        }
    }
}

