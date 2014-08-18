using NLog;
using System;
using System.IO;
using System.Printing;
using System.Threading.Tasks;
using System.Windows.Documents;
using System.Windows.Markup;
using System.Windows.Media.Imaging;
using System.Xml;

using checkin.core.support;
using checkin.presentation.gui.control;
using System.Windows.Shapes;
using checkin.core.models;
using checkin.core.events;

namespace checkin.presentation.models
   {
    public class TicketXamlPrinting :ITicketPrinting
    {
        public IResource Resource { get; set; }

        private LocalPrintServer ps;
        private Logger logger = LogManager.GetCurrentClassLogger();

        //temporary variable
        public TicketXamlPrinting (IResource resource)
        {
            Resource = resource;
            this.ps = new LocalPrintServer();
            this.DefaultPrinter = this.ps.DefaultPrintQueue;
        }

        //TODO:move
        public void EmitQRCodeIfExists(FixedDocument doc)
        {
            foreach (var p in doc.Pages)
            {
                var qr = WpfUtilEx.FindVisualChild<QRCodeCanvas>(p.Child);
                if (qr != null)
                {
                    qr.RaiseEvent(new System.Windows.RoutedEventArgs(QRCodeCanvas.LoadedEvent));
                    p.Child.Children.Add(new Rectangle()); // dummy;
                }
            }
        }

        //TODO:move
        public string NormalizedXaml(string xaml)
        {
            // Convert From:
            //<@qrclass@ xmlns:@ns@="clr-namespace:@fullns;assembly=@ns" 
            // To:
            //<QR:QRCodeCanvas xmlns:QR="clr-namespace:checkin.presentation.gui.control;assembly=QR"
            xaml = xaml.Replace("@fullns@", "@ns@.presentation.gui.control");
            xaml = xaml.Replace("@qrclass@", "@ns@:QRCodeCanvas");
            // this is sooooooooooooooooooooo ugly.
            xaml = xaml.Replace("@ns@", "checkin");
            xaml = xaml.Replace("assembly=checkin", "assembly=checkin-presentation");
            //xaml = ReplaceExecutableNamespaceName.Replace(xaml, "@ns@");
            return xaml;
        }

        #region ITicketPrinting implementation
        public PrintQueue DefaultPrinter { get; set; }

        public bool EnqueuePrinting (TicketImageData imageData, IInternalEvent ev)
        {

            PrintQueue pq = this.DefaultPrinter;
            var writer = PrintQueue.CreateXpsDocumentWriter(pq);

            //@ns@ÇassemblyñºÇ…ïœä∑ÇµÇƒÇ©ÇÁì«Ç›çûÇﬁ
            var xmlreader = XmlReader.Create(new StringReader(this.NormalizedXaml(imageData.xaml)));

            //xamlÇobjectâªÇ≈Ç´ÇÈÇÃÇÕui thread ÇÃÇ›
            FixedDocument doc = ev.CurrentDispatcher.Invoke<FixedDocument>(() =>
            {
                return XamlReader.Load(xmlreader) as FixedDocument;
            }, System.Windows.Threading.DispatcherPriority.Send);

            //QRÇÃéwíËÇ™Ç™Ç†Ç¡ÇΩÇ∆Ç´Ç…ÇÕÅAQRÇñÑÇﬂçûÇﬁ
            this.EmitQRCodeIfExists(doc);

            writer.Write(doc, pq.UserPrintTicket);
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
        }
        #endregion
    }
    
}
