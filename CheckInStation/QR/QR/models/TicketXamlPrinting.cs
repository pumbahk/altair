using NLog;
using System;
using System.IO;
using System.Printing;
using System.Threading.Tasks;
using System.Windows.Documents;
using System.Windows.Markup;
using System.Windows.Media.Imaging;
using System.Xml;

using QR.support;
using Microsoft.TeamFoundation.Controls.WPF;
using QR.presentation.gui.control;
using System.Windows.Shapes;

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

        //TODO:move
        public void EmitQRCodeIfExists(FixedDocument doc)
        {
            foreach (var p in doc.Pages)
            {
                var qr = WpfUtil.FindVisualChild<QRCodeCanvas>(p.Child);
                if (qr != null)
                {
                    qr.RaiseEvent(new System.Windows.RoutedEventArgs(QRCodeCanvas.LoadedEvent));
                    p.Child.Children.Add(new Rectangle()); // dummy;
                }
            }
        }

        #region ITicketPrinting implementation
        public PrintQueue DefaultPrinter { get; set; }

        public async Task<bool> EnqueuePrinting (TicketImageData imageData, IInternalEvent ev)
        {

            PrintQueue pq = this.DefaultPrinter;
            this.writer = PrintQueue.CreateXpsDocumentWriter(pq);

            //@ns@��assembly���ɕϊ����Ă���ǂݍ���
            var r = new StringReader(InjectExecutableNamespaceName.Inject(imageData.xaml, "@ns@"));
            var xmlreader = XmlReader.Create(r);

            //xaml��object���ł���̂�ui thread �̂�
            FixedDocument doc = await ev.CurrentDispatcher.InvokeAsync<FixedDocument>(() =>
            {
                return XamlReader.Load(xmlreader) as FixedDocument;
            }, System.Windows.Threading.DispatcherPriority.Send);

            //QR�̎w�肪���������Ƃ��ɂ́AQR�𖄂ߍ���
            this.EmitQRCodeIfExists(doc);

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
