using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Documents;
using System.Xaml;

namespace AltairXamlView
{
    /// <summary>
    /// App.xaml の相互作用ロジック
    /// </summary>
    public partial class App : Application
    {
        string[] arguments;

        public void Application_StartUp(object sender, StartupEventArgs e)
        {
            arguments = e.Args;
        }

        private void Application_Activated(object sender, EventArgs e)
        {
            Console.WriteLine(arguments[0]);
            Console.WriteLine(MainWindow);
            if (arguments.Length > 0)
            {
                var xxr = new XamlXmlReader(arguments[0]);
                var xow = new XamlObjectWriter(xxr.SchemaContext);
                while (xxr.Read())
                {
                    xow.WriteNode(xxr);
                }
                Console.WriteLine(xow.Result);
                ((MainWindow)(this.MainWindow)).GetDocumentViewer().Document = (FixedDocument)xow.Result;
            }
        }
    }
}
