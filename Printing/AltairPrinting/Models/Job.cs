using System.IO;
using System.Xml;
using System.Windows.Markup;
using System.Windows.Documents;

namespace AltairPrinting.Altair.Document
{
    class Job
    {
        public string PrinterName { get; set; }
        public FixedDocument Document { get; set; }
        private string xaml;

        public Job(FixedDocument document)
        {
            this.Document = document;
        }

        public Job(string xaml)
        {
            this.xaml = xaml;
        }

        public void Build()
        {
            if (xaml != null)
            {
                Document = XamlReader.Load(XmlReader.Create(new StringReader(xaml))) as FixedDocument;
            }
        }
    }
}
